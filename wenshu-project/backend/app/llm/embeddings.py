"""向量模型客户端。

provider:
- relay：经中转站调用 bge-m3（默认）
- local：本地 sentence-transformers（离线 fallback）
- hash ：确定性哈希向量（仅开发/测试，无网络可用）
"""
from __future__ import annotations
from typing import Optional

import hashlib
import math
import re
import time
from collections import OrderedDict
from app.llm.privacy import redact

from app.config import Settings
from app.llm.relay import RelayClient
from app.llm.client import LLMError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingClient:
    def __init__(self, settings: Settings, relay: Optional[RelayClient] = None) -> None:
        self.settings = settings
        self.provider = settings.embedding_provider.lower()
        self.model = settings.embedding_model
        self.dim = settings.embedding_dim
        self.relay = relay
        self._local_model = None
        self._query_cache = OrderedDict()
        self._query_cache_limit = 1024
        self._query_cache_ttl = 3600

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self.provider == "hash":
            return [self._hash_embed(t) for t in texts]
        if self.provider == "local":
            import asyncio
            return await asyncio.to_thread(self._local_embed, texts)
        if self.provider != "relay":
            raise LLMError(f"未知Embedding provider: {self.provider}")
        if self.relay is None or not self.settings.relay_api_key:
            raise LLMError("真实Embedding未配置凭证，禁止混入hash向量")
        output = []
        for start in range(0, len(texts), 10):
            batch = texts[start:start + 10]
            vecs = await self.relay.embed(batch, model=self.model)
            if len(vecs) != len(batch) or any(len(v) != self.dim for v in vecs):
                raise LLMError("Embedding批次条数或向量维度与配置不符")
            if any(not math.isfinite(float(x)) for v in vecs for x in v):
                raise LLMError("Embedding包含非有限数值")
            output.extend(vecs)
        return output

    async def embed_query(self, text: str) -> list[float]:
        # 模型/维度/部署地址与脱敏后的文本共同决定缓存签名。
        signature = f"{self.provider}:{self.model}:{self.dim}:{self.settings.relay_base_url}:" + redact(text)
        key = hashlib.sha256(signature.encode()).hexdigest()
        cached = self._query_cache.get(key)
        if cached and cached[0] > time.monotonic():
            self._query_cache.move_to_end(key)
            return list(cached[1])
        vecs = await self.embed([text])
        self._query_cache[key] = (time.monotonic()+self._query_cache_ttl,list(vecs[0]))
        self._query_cache.move_to_end(key)
        while len(self._query_cache)>self._query_cache_limit:
            self._query_cache.popitem(last=False)
        return list(vecs[0])

    def _local_embed(self, texts: list[str]) -> list[list[float]]:
        try:
            from sentence_transformers import SentenceTransformer  # 延迟导入，可选依赖
        except ImportError:
            raise LLMError("未安装本地Embedding依赖，禁止混入hash向量")
        if self._local_model is None:
            self._local_model = SentenceTransformer(self.model)
        vecs = self._local_model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vecs]

    def _hash_embed(self, text: str) -> list[float]:
        """确定性哈希向量：对字符 n-gram 做 hashing 得到稀疏向量，再归一化。

        仅用于离线开发/测试，不具备真实语义，但保证 cosine 可计算且文本相似者相近。
        """
        text = self._normalize(text)
        dim = max(self.dim, 128)
        vec = [0.0] * dim
        ngrams = [text]
        if len(text) > 2:
            ngrams += [text[i : i + 2] for i in range(len(text) - 1)]
        for ng in ngrams:
            for suffix in ("", " "):
                h = hashlib.md5((ng + suffix).encode("utf-8")).digest()
                idx = int.from_bytes(h[:4], "big") % dim
                sign = 1.0 if h[4] % 2 == 0 else -1.0
                vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    @staticmethod
    def _normalize(text: str) -> str:
        text = re.sub(r"\s+", "", text)
        return text.lower()
