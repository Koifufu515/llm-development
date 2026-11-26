"""从父块正文里抽取易变数值，写入 fact_mentions。只在离线脚本里运行，不在查询链路上。"""
from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from uuid import UUID

from openai import AsyncOpenAI

from quarry.facts.contract import check_item, norm_entity
from quarry.infra.db import acquire
from quarry.infra.logging import get_logger
from quarry.infra.settings import Settings

log = get_logger()

SYSTEM_PROMPT = """你是旅游攻略的数值抽取器。从用户给出的一段攻略里，找出下面两类数值：
- ticket_price：景点门票价格（人民币，成人全价票；免费写 0）
- open_hours：景点开放时间

只输出一个 JSON 对象，格式如下：
{"items": [{"entity": "景点全名", "attribute": "ticket_price", "qualifier": "全年", "value": "120", "quote": "120 元"}]}

规则：
1. entity 写景点全名。正文里没写景点名时，从标题路径里取。
2. qualifier 只能是"全年""旺季""淡季"之一。分季节的分开写，夏季算旺季，冬季算淡季。
3. value：价格只写数字；开放时间写成 HH:MM-HH:MM（24 小时制）。
4. quote 从原文逐字复制，只包含表示这个数值的最短片段，例如"120 元""8:30 至 18:00"。
5. 学生票、儿童票等优惠票，以及交通、住宿、餐饮的价格都不要抽。
6. 港币、美元、新台币等非人民币门票不要抽；船票、交通套票即使含景区门票也不要当景区门票。
7. 同一段有多个景点和相同数值时，逐条核对实体及其自己的那一处原文，不得把别的景点数值绑定过来。
8. 一个都没有时，输出 {"items": []}。"""

# 粗筛：连"数字+元""几点几分"这类样子都没有的块，不送模型
CANDIDATE = re.compile(r"\d\s*元|[¥￥]\s*\d|免费|\d{1,2}\s*[:：]\s*\d{2}|\d{1,2}\s*点")

_TODO_SQL = """
SELECT c.chunk_id, c.heading_path, c.content
FROM chunks c
JOIN documents d ON d.id = c.document_id
WHERE c.collection_id = $1
  AND c.level = 0
  AND d.status = 'ready'
  AND NOT EXISTS (SELECT 1 FROM fact_extractions e
                  WHERE e.collection_id = c.collection_id AND e.chunk_id = c.chunk_id)
ORDER BY c.chunk_id
"""

_INSERT_SQL = """
INSERT INTO fact_mentions (collection_id, chunk_id, span_start, span_end, entity_name,
                           entity_norm, attribute, qualifier, value, quote)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
"""

_RECORD_SQL = """
INSERT INTO fact_extractions (collection_id, chunk_id, model, mention_count)
VALUES ($1, $2, $3, $4)
ON CONFLICT (collection_id, chunk_id)
DO UPDATE SET model = EXCLUDED.model, mention_count = EXCLUDED.mention_count,
              extracted_at = now()
"""

@dataclass
class Stats:
    todo: int = 0             # 还没抽过的父块
    skipped: int = 0          # 粗筛没过，直接记为抽出 0 条
    called: int = 0           # 调了模型的块
    failed: int = 0
    mentions: int = 0
    dropped: dict[str, int] = field(default_factory=dict)

def make_client(s: Settings) -> AsyncOpenAI:
    # FACT_API_KEY 留空时复用 LLM_API_KEY
    key = s.fact_api_key.get_secret_value() or s.llm_api_key.get_secret_value()
    if not s.fact_model or not s.fact_base_url:
        raise ValueError("先在 .env 里配置 FACT_MODEL 和 FACT_BASE_URL")
    if not key or "REPLACE-ME" in key:
        raise ValueError("没有可用的 API Key：先填好 LLM_API_KEY，或单独填 FACT_API_KEY")
    return AsyncOpenAI(base_url=s.fact_base_url, api_key=key,
                       timeout=s.fact_timeout_s, max_retries=2)

async def call_model(client: AsyncOpenAI, model: str, heading_path: list[str],
                     content: str) -> list:
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",
             "content": f"标题路径：{' > '.join(heading_path)}\n\n正文：\n{content}"},
        ],
        response_format={"type": "json_object"},        # JSON 模式：提示词里必须出现 JSON 这个词
        temperature=0,
        extra_body={"enable_thinking": False},          # JSON 模式不能和思考模式同时开
    )
    data = json.loads(resp.choices[0].message.content or "{}")
    items = data.get("items") if isinstance(data, dict) else None
    return items if isinstance(items, list) else []

def to_mentions(items: list, content: str, stats: Stats) -> list[dict]:
    """逐条校验，并在原文里找到 quote 的位置。位置由代码来找，不让模型报偏移。"""
    taken: list[tuple[int, int]] = []
    out: list[dict] = []
    for raw in items:
        item, reason = check_item(raw)
        if item is None:
            stats.dropped[reason] = stats.dropped.get(reason, 0) + 1
            continue
        if item["attribute"] == "ticket_price" and re.search(r"HK\$|HKD|NT\$|USD|港[币幣]|[新台臺]{2,3}[币幣]|\$", item["quote"], re.I):
            stats.dropped["非人民币票价"] = stats.dropped.get("非人民币票价", 0) + 1
            continue
        if item["attribute"] == "ticket_price":
            # 组合交通票与有明确子景点名称的票价不能改挂在父景点名下。
            named = re.search(r"^([\u4e00-\u9fff]{2,16})门票", item["quote"])
            if re.search(r"—|→|--", item["entity"]) or (named and named[1] not in {"成人","全价","全票","景区","景点","全年","旺季","淡季","每位成人","单人"} and norm_entity(named[1]) not in norm_entity(item["entity"])):
                stats.dropped["票价实体或交通类型不符"] = stats.dropped.get("票价实体或交通类型不符", 0) + 1
                continue
        start = _find_owned_quote(content, item["quote"], item["entity"], taken)
        if start is None:
            stats.dropped["原文里找不到"] = stats.dropped.get("原文里找不到", 0) + 1
            continue
        end = start + len(item["quote"])
        taken.append((start, end))
        out.append({**item, "span_start": start, "span_end": end,
                    "entity_norm": norm_entity(item["entity"])})
    return out

async def save(collection_id: UUID, chunk_id: str, model: str,
               mentions: list[dict]) -> None:
    """一个块的结果在一个事务里写完：删掉旧提及，写入新提及，记一笔抽取记录。"""
    async with acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "DELETE FROM fact_mentions WHERE collection_id = $1 AND chunk_id = $2",
                collection_id, chunk_id)
            if mentions:
                await conn.executemany(_INSERT_SQL, [
                    (collection_id, chunk_id, m["span_start"], m["span_end"], m["entity"],
                     m["entity_norm"], m["attribute"], m["qualifier"], m["value"], m["quote"])
                    for m in mentions])
            await conn.execute(_RECORD_SQL, collection_id, chunk_id, model, len(mentions))

async def extract_collection(s: Settings, collection_id: UUID, *,
                             limit: int | None = None, dry_run: bool = False) -> Stats:
    client = make_client(s)                             # 配置有问题，在这里就报出来
    async with acquire() as conn:
        blocks = await conn.fetch(_TODO_SQL, collection_id)

    stats = Stats(todo=len(blocks))
    plain = [b for b in blocks if not CANDIDATE.search(b["content"])]
    candidates = [b for b in blocks if CANDIDATE.search(b["content"])][:limit]
    stats.skipped = len(plain)
    if plain and not dry_run:
        async with acquire() as conn:
            await conn.executemany(
                _RECORD_SQL,
                [(collection_id, b["chunk_id"], "prefilter", 0) for b in plain])

    sem = asyncio.Semaphore(s.fact_concurrency)         # 并发上限，防止触发接口限流

    async def one(b) -> None:
        try:
            async with sem:
                stats.called += 1
                items = await call_model(client, s.fact_model,
                                         list(b["heading_path"]), b["content"])
            mentions = to_mentions(items, b["content"], stats)
            if dry_run:
                _print_block(b, mentions)
            else:
                await save(collection_id, b["chunk_id"], s.fact_model, mentions)
            stats.mentions += len(mentions)
        except Exception as e:
            stats.failed += 1
            log.warning("抽取失败 {}：{!r}", b["chunk_id"][:8], e)   # 不记录，下次运行会重试

    await asyncio.gather(*(one(b) for b in candidates))
    return stats

def _find_owned_quote(content: str, quote: str, entity: str,
                      taken: list[tuple[int, int]]) -> int | None:
    """重复数值不能靠模型输出顺序认领：优先在实体自己的行内定位。

    标题中给出的实体可能不在正文；仅一个未占用原文位置时保留原契约，
    多个位置且无法证明归属则丢弃，绝不将其静默绑定到第一个景点。
    """
    candidates = [m.start() for m in re.finditer(re.escape(quote), content)
                  if all(m.end() <= a or m.start() >= b for a,b in taken)]
    names = [m for m in re.finditer(re.escape(entity), content)]
    # 名字在另一条目的地址/介绍里出现，不代表该条目的数值归它。
    header_names = [m for m in names if not re.search(r"[，。,]", content[content.rfind("\n", 0, m.start())+1:m.start()])]
    if header_names:
        names = header_names
    owned = []
    for name in names:
        line_end = content.find("\n", name.end())
        line_end = len(content) if line_end < 0 else line_end
        owned += [(start-name.end(),start) for start in candidates
                  if name.end() <= start < line_end]
    if owned:
        return min(owned)[1]
    # 实体名独占一行时，描述可以在紧接着的段落；不越过空行/下一条目。
    for name in names:
        tail = content[name.end():]
        stop = re.search(r"\n\s*\n|\n\s*\d+\s+", tail)
        end = name.end() + stop.start() if stop else len(content)
        after = [start for start in candidates if name.end() <= start < end]
        if after:
            return min(after)
    if not names and len(candidates) == 1:
        return candidates[0]
    return None

def _find_free(content: str, quote: str, taken: list[tuple[int, int]]) -> int | None:
    """找 quote 在原文里第一次出现、并且不和已认领片段重叠的位置。"""
    start = content.find(quote)
    while start != -1:
        end = start + len(quote)
        if all(end <= s or start >= e for s, e in taken):
            return start
        start = content.find(quote, start + 1)
    return None

def _print_block(b, mentions: list[dict]) -> None:
    print(f"\n■ {' > '.join(b['heading_path'])}  ({b['chunk_id'][:8]})")
    if not mentions:
        print("  （没有抽到）")
    for m in mentions:
        print(f"  {m['attribute']:<13}{m['qualifier']}  {m['value']:<12} "
              f"← 「{m['quote']}」  {m['entity']}")
