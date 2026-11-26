"""K8s 部门 Agent 客户端：Service Discovery、并发调用和部分成功。"""
from __future__ import annotations

import asyncio
import re
from typing import Any

import httpx

from app.config import Settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DepartmentAgentClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    def _http(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(trust_env=False,limits=httpx.Limits(max_connections=100,max_keepalive_connections=50))
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client=None

    @property
    def enabled(self) -> bool:
        return self.settings.dept_agents_enabled and not self.settings.dept_id

    @staticmethod
    def slug(dept_id: str) -> str:
        return dept_id.removeprefix("dept_").replace("_", "-")

    def url(self, dept_id: str) -> str:
        if not re.fullmatch(r"dept_[A-Za-z0-9_-]{1,64}",dept_id):
            raise ValueError("非法部门ID，禁止构造任意主机地址")
        return self.settings.dept_agent_url_template.format(
            dept_id=dept_id, slug=self.slug(dept_id)
        ).rstrip("/")

    async def answer_many(
        self, query: str, dept_ids: list[str], session_id: str, user_id: str, memory_context: str = "", user_role: str = "student"
    ) -> tuple[list[dict[str, Any]], list[str]]:
        raw = await asyncio.gather(
            *(self._answer_one(query, dept, session_id, user_id, memory_context, **({"user_role":user_role} if user_role!="student" else {})) for dept in dept_ids),
            return_exceptions=True,
        )
        results: list[dict[str, Any]] = []
        failed: list[str] = []
        for dept, item in zip(dept_ids, raw):
            if isinstance(item, BaseException) or item is None:
                failed.append(dept)
                if isinstance(item, BaseException):
                    logger.warning("部门 Agent %s 调用失败: %s", dept, item)
            else:
                results.append(item)
        return results, failed

    async def _answer_one(
        self, query: str, dept_id: str, session_id: str, user_id: str, memory_context: str = "", user_role: str = "student"
    ) -> dict[str, Any] | None:
        timeout = httpx.Timeout(
            self.settings.dept_agent_timeout, connect=self.settings.dept_agent_partial_timeout
        )
        response = await self._http().post(
            f"{self.url(dept_id)}/api/v1/internal/dept/answer",
            headers={"X-Internal-Token": self.settings.internal_api_token},
            timeout=timeout,
            json={
                "query": query, "dept_id": dept_id, "user_id": user_id,
                "session_id": f"{session_id}:{dept_id}",
                "memory_context": memory_context,"user_role":user_role,"parent_session_id":session_id,
            },
        )
        response.raise_for_status()
        body = response.json()
        return body.get("data") if body.get("code") == 0 else None
