"""Retrieval Agent：执行混合检索（BM25 + 向量 + Rerank），返回 top-k chunks。"""
from __future__ import annotations
from app.memory.facts import document_readable
from app.utils.telemetry import operation_span

from typing import Any, Optional
import asyncio

from app.llm.embeddings import EmbeddingClient
from app.retrieval.hybrid import HybridRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RetrievalAgent:
    def __init__(self, hybrid: HybridRetriever, embeddings: EmbeddingClient, store) -> None:
        self.hybrid = hybrid
        if isinstance(hybrid, HybridRetriever):
            hybrid.store = store
        self.embeddings = embeddings
        self.store = store

    @operation_span("retrieval.hybrid")
    async def retrieve(self, queries: list[str], dept_ids: Optional[list[str]] = None, top_k: int = 5, user_role: str = "student") -> list[dict[str, Any]]:
        """多 query × 多部门并行检索，合并去重。"""
        if not queries:
            return []
        dept_ids = dept_ids or [None]
        seen: dict[str, dict[str, Any]] = {}

        semaphore = asyncio.Semaphore(8)
        async def one_query(query):
            async with semaphore:
                try:
                    vec = await self.embeddings.embed_query(query)
                except Exception as exc:
                    logger.warning("查询Embedding不可用，使用BM25: %s", type(exc).__name__)
                    vec = []
                groups = await asyncio.gather(*[
                    self.hybrid.retrieve(query, vec, dept_id=None if d == "dept_all" else d, **({"user_role":user_role} if isinstance(self.hybrid,HybridRetriever) else {}))
                    for d in dept_ids
                ], return_exceptions=True)
                return [hit for group in groups if isinstance(group, list) for hit in group]
        for group in await asyncio.gather(*[one_query(q) for q in dict.fromkeys(queries)]):
            for hit in group:
                id_ = hit.get("id", "")
                if id_ and (id_ not in seen or hit.get("rerank_score", 0) > seen[id_].get("rerank_score", 0)):
                    seen[id_] = hit

        # 检索后统一从持久化存储回填完整 chunk，避免向量库只返回 metadata
        # 导致正文、关键词和章节信息缺失；同时在返回前强制校验文档仍为 active。
        chunks: list[dict[str, Any]] = []
        for chunk_id, hit in seen.items():
            stored = await self.store.get("chunks", chunk_id)
            if not stored:
                continue
            doc = await self.store.get_document(stored.get("doc_id", ""))
            if not document_readable(doc,user_role):
                continue
            if user_role not in doc.get("access_roles",["student","teacher","admin"]):
                continue
            allowed = set(dept_ids) - {None, "dept_all"}
            if allowed and (stored.get("dept_id") not in allowed or doc.get("dept_id") not in allowed):
                continue
            full = dict(hit)
            full.update(stored)
            full["id"] = chunk_id
            full["doc_title"] = doc.get("title", "")
            chunks.append(full)
        chunks.sort(key=lambda x: x.get("rerank_score", x.get("_rrf", x.get("score", 0.0))), reverse=True)
        return chunks[:top_k]
