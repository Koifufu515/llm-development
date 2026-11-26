"""原0144/0673/0154入参上下文与12行紧凑结果；同一包装对象注册和执行。"""
"""
MCP 工具筛选器
按需获取特定类型的 MCP 工具
"""
import ast
import contextvars
import json
import re
from datetime import date as _date
from typing import Any, List
from langchain_core.tools import BaseTool
import logging
app_logger=logging.getLogger(__name__)

# ===== 工具入参代码层兜底（准则：不允许只靠提示词保证参数合法） =====
# 实测模型调 get-tickets 时漏传 fromStation/toStation、或把日期写成 trainDate，12306 直接
# -32602 拒绝 → 该段降级"实时班次暂不可用"。prompt 里写参数名不可靠（用户明确准则），
# 故在工具层做确定性处理：① 别名归一 ② 用本轮上下文回填 ③ 仍缺则返回可读提示。
# 上下文用 contextvar（按请求任务隔离，不跨会话污染）；由 middleware 每轮写入。
_TURN_CTX: contextvars.ContextVar[dict] = contextvars.ContextVar("tool_arg_ctx", default={})

_TRAIN_ARG_ALIAS = {
    # 日期别名
    "trainDate": "date", "departureDate": "date", "travelDate": "date",
    "dateStr": "date", "startDate": "date", "departureTime": "date",
    # 出发站别名
    "from": "fromStation", "fromStationName": "fromStation", "startStation": "fromStation",
    "fromCity": "fromStation", "departure": "fromStation", "departureStation": "fromStation",
    # 到达站别名
    "to": "toStation", "toStationName": "toStation", "endStation": "toStation",
    "toCity": "toStation", "arrival": "toStation", "arrivalStation": "toStation",
}

# ★ 中间件每轮写一次：本轮已知的出发地 / 目的地 / 日期 / 当前段，供车票守卫回填入参
def set_turn_context(
        departure_city: str = "", destination: str = "", date: str = "",
        multi_leg: bool = False, leg_from: str = "", leg_to: str = ""
) -> None:
    """由中间件每轮写入本轮已知信息（出发地/目的地/出发日期/是否多段/当前段起），供工具入参回填"""
    _TURN_CTX.set({
        "departure_city": departure_city or "",
        "destination": destination or "",
        "date": date or "",
        "multi_leg": bool(multi_leg),
        # 多目的地段级循环下，"当前待确认段"的起讫站是参数的权威来源——
        # 由段游标（代码）给出，模型漏传时按此回填，保证"一次只查当前段"
        "leg_from": leg_from or "",
        "leg_to": leg_to or "",
    })

def _normalize_train_args(kwargs: dict) -> dict | str:
    """交通查询入参归一：别名纠正 → 缺失回填 → 仍缺返回可读提示（不再抛底层 MCP 报错）"""
    args = dict(kwargs or {})
    for k in list(args):
        canon = _TRAIN_ARG_ALIAS.get(k)
        if not canon:
            continue
        if not args.get(canon):
            args[canon] = args[k]
        args.pop(k, None)               # 别名键必须移除（服务端 schema 禁止多余字段）
    ctx = _TURN_CTX.get() or {}
    if not args.get("date") and ctx.get("date"):
        args["date"] = ctx["date"]
    if not ctx.get("multi_leg"):        # 多段时严禁猜测起讫站，否则会查到错误路段
        if not args.get("fromStation") and ctx.get("departure_city"):
            args["fromStation"] = ctx["departure_city"]
        if not args.get("toStation") and ctx.get("destination"):
            args["toStation"] = ctx["destination"]
    else:
        # 多段模式下**日期也按段定**，模型传的日期一律覆盖——实测它对三段
        # 城际全填出发日（09-18），导致"同一天既在重庆又在北京"的荒谬时序；段日期由中间件
        # 按城市天数分配算出，此处只认上下文里的权威值
        if ctx.get("date"):
            args["date"] = ctx["date"]
        # 多段模式改为"按段游标回填当前段"——不再要求模型补全（它补的往往是
        # 编造的段），只要中间件写入了当前段起讫站，就补齐缺失站名，确保查的是正在确认的那一段
        if not args.get("fromStation") and ctx.get("leg_from"):
            args["fromStation"] = ctx["leg_from"]
        if not args.get("toStation") and ctx.get("leg_to"):
            args["toStation"] = ctx["leg_to"]
    missing = [k for k in ("date", "fromStation", "toStation") if not args.get(k)]
    if missing:
        return (
            f"【调用参数不完整】缺少 {' / '.join(missing)}。请补全后重新调用本工具："
            "fromStation=出发站中文名，toStation=到达站中文名，date=YYYY-MM-DD。"
        )
    # 日期必须不是过去——实测模型（Qwen）日期感错乱，在需求收集轮自行
    # 调用 get-tickets 时传了过去的日期，12306 直接拒绝，用户看到"查询时出现了一个错误，
    # 看起来是由于选择了过去的日期"。提示词约束不住（用户准则），此处做确定性拦截：
    # 过去日期一律不发给服务端，也不猜测替代值（改动用户日期更危险），交由模型向用户确认
    try:
        if _date.fromisoformat(str(args["date"])[:10]) < _date.today():
            app_logger.warning(f"⚠️ {args['date']} 是过去的日期，已拦下（12306 不查历史班次）")
            return (f"【日期无效】{args['date']} 已是过去的日期，12306 只能查询今天及之后的班次。"
                    "请先向用户确认出发日期，再用今天或之后的日期（YYYY-MM-DD）重新调用。")
    except ValueError:
        pass
    return args


# ===== 车票结果代码层裁剪（防"4.5 万字淹没"）=====
# 实测 12306 单次返回 287 趟/45,633 字，模型被淹没后编造出 G1001/G1003/G1005（¥154.5，
# 真实数据里不存在）。提示词约束不住数据量，故在工具层做确定性裁剪：解析真实班次 →
# 按发车时间排序 → 只保留前 N 趟 → 一行一趟（含席别票价）。模型只看到十几行，无从淹没。
_TRAIN_ROW_RE = re.compile(
    r"^([A-Z]\d{1,4})\s+(.+?)\(telecode:[^)]*\)\s*->\s*(.+?)\(telecode:[^)]*\)\s+"
    r"(\d{2}:\d{2})\s*->\s*(\d{2}:\d{2})\s+历时：(\d{1,2}:\d{2})",
    re.MULTILINE,
)
_SEAT_RE = re.compile(r"^-\s*([^:：]+)[:：]\s*(\S+)\s+([\d.]+)元", re.MULTILINE)
# 裁剪后的紧凑行：车次|出发→到达|出发→到达时刻|历时|席别票价（同时供 chat 层回读校验）
_COMPACT_ROW_RE = re.compile(
    r"^([A-Z]\d{1,4})\|([^|\n]+?)→([^|\n]+?)\|(\d{2}:\d{2})→(\d{2}:\d{2})\|"
    r"(\d{1,2}:\d{2})\|([^|\n]+)$",
    re.MULTILINE,
)
_SEAT_ORDER = ("二等座", "硬座", "一等座", "硬卧", "软卧", "无座")
# 这个是最多显示多少个高铁，因为有一些高铁会显示非常多，直接给你撑爆了，你可以自行调整
_TICKET_LIMIT = 12

def _raw_text(raw: Any) -> str:
    """MCP 返回可能是 content blocks 列表，统一取纯文本"""
    if isinstance(raw, list):
        return "\n".join(b.get("text", "") for b in raw if isinstance(b, dict))
    return str(raw or "")

def parse_ticket_rows(raw: Any) -> list[dict]:
    """解析 12306 原始返回：每趟车一条记录（车次/区间/时刻/历时/各席别票价）"""
    text = _raw_text(raw)
    rows: list[dict] = []
    hits = list(_TRAIN_ROW_RE.finditer(text))
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        seats = {
            s.group(1).strip(): (s.group(2).strip(), float(s.group(3)))
            for s in _SEAT_RE.finditer(text[m.end():end])
        }
        rows.append({
            "code": m.group(1), "from": m.group(2).strip(), "to": m.group(3).strip(),
            "dep": m.group(4), "arr": m.group(5), "dur": m.group(6), "seats": seats,
        })
    return rows

def parse_compact_rows(text: Any) -> list[dict]:
    """解析裁剪后的紧凑班次行（供页面展示层回读真实数据做权威清单）"""
    return [
        {"code": m.group(1), "from": m.group(2), "to": m.group(3), "dep": m.group(4),
         "arr": m.group(5), "dur": m.group(6), "seat": m.group(7)}
        for m in _COMPACT_ROW_RE.finditer(_raw_text(text))
    ]

def compact_ticket_text(raw: Any, limit: int = _TICKET_LIMIT) -> str:
    """把车票查询结果压成"一行一趟"（按发车时间升序取前 limit 趟）；解析失败则截断降级"""
    rows = parse_ticket_rows(raw)
    if not rows:
        return _raw_text(raw)[:2000]
    rows.sort(key=lambda r: r["dep"])
    shown = rows[:limit]
    lines = [
        f"实时班次（共 {len(rows)} 趟，按发车时间排序，仅列前 {len(shown)} 趟）：",
        "格式：车次|区间|出发→到达|历时|票价",
    ]
    for r in shown:
        seat = next((k for k in _SEAT_ORDER if k in r["seats"]), None)
        price = (
            f"{seat} {r['seats'][seat][0]} {r['seats'][seat][1]:g}元"
            if seat else "票价未返回"
        )
        lines.append(f"{r['code']}|{r['from']}→{r['to']}|{r['dep']}→{r['arr']}|{r['dur']}|{price}")
    app_logger.info(
        f"✂️ 车票结果裁剪：原始 {len(_raw_text(raw))} 字/{len(rows)} 趟 → "
        f"压缩 {len(chr(10).join(lines))} 字/{len(shown)} 趟"
    )
    return "\n".join(lines)


class _ArgGuardTool(BaseTool):
    """ 入参兜底包装（name/description/args_schema 原样透传，仅拦截调用入参）"""
    name: str
    description: str
    inner: Any = None

    def _run(self, *args, **kwargs):
        raise NotImplementedError("仅支持异步调用")

    async def _arun(self, **kwargs):
        args = _normalize_train_args(kwargs)
        if isinstance(args, str):
            app_logger.warning(f"⚠️ {self.name} 入参不完整，已拦下并提示补全：{kwargs}")
            return args
        # ★ 只拦截入参：纠正、回填之后交给原工具去查
        result = await self.inner.ainvoke(args)
        # 结果裁剪后再交给模型（防海量班次淹没上下文诱发编造）
        # ★ 结果顺手压成"一行一趟"：模型看得清，上下文也不会被撑爆
        return compact_ticket_text(result)

def _guard_train_tool(tool: BaseTool) -> BaseTool:
    """仅包装"必填 date/fromStation/toStation"的车票查询工具（按 schema 判定，不写死工具名）"""
    schema = tool.args_schema if isinstance(tool.args_schema, dict) else {}
    # ★ 按 schema 认车票工具，不写死工具名
    if not {"date", "fromStation", "toStation"} <= set(schema.get("required") or []):
        return tool
    return _ArgGuardTool(
        name=tool.name, description=tool.description,
        args_schema=tool.args_schema, inner=tool,
    )

def apply_train_arg_guard(tools: List[BaseTool]) -> List[BaseTool]:
    """ 对全量工具套用车票守卫（注册侧同源，供 create_agent 使用）

    A 的包装此前只作用于 get_train_tools() 的返回值——那是 middleware 注入给模型
    "看"的一份；而 LangGraph 的 ToolNode 是按工具名到 create_agent(tools=...) 的注册表里取对象
    **执行**的，那里注册的是 get_all_mcp_tools() 的原始工具。两者不是同一批对象，
    导致参数兜底与结果裁剪在真实跑图时被整体绕过（实测：跑图时 ToolMessage 是 39,265 字
    12306 原文、日志无"车票结果裁剪"，并因此撑爆模型 30720 输入上限）。
    """
    return [_guard_train_tool(t) for t in tools]
