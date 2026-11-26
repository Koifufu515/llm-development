"""pi Agent Runtime 客户端。

Python 负责控制平面、事实和记忆治理；本客户端只把已治理的概率性执行请求交给 pi。
失败返回 None，由各 Python Agent 使用现有本地 LLM/规则实现降级。
"""
from __future__ import annotations
from app.utils.telemetry import operation_span

from typing import Any, Literal, Optional

import httpx
import json
import time

from app.config import Settings
from app.llm.privacy import redact
from app.llm.usage import record
from app.utils.logging import get_logger
from app.utils import metrics

logger = get_logger(__name__)

AgentType = Literal["intent", "rewrite", "answer", "verify", "reflect"]
OutputMode = Literal["text", "json"]


class PiAgentRuntimeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = settings.pi_agent_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
        self._failures = 0
        self._open_until = 0.0
        self._probe = False

    def _enter_circuit(self):
        if self._failures < 3:return True
        if time.monotonic() < self._open_until or self._probe:return False
        self._probe = True
        return True

    def _circuit_result(self, success):
        self._probe = False
        if success:
            self._failures = 0
            self._open_until = 0.0
        else:
            self._failures += 1
            if self._failures >= 3:self._open_until = time.monotonic()+30

    @property
    def enabled(self) -> bool:
        return self.settings.pi_agent_enabled and bool(self.base_url) and bool(self.settings.internal_api_token)

    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.settings.pi_agent_timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @operation_span("pi.execute")
    async def run(
        self, agent_type: AgentType, system_prompt: str, prompt: str,
        output_mode: OutputMode = "json", allowed_tools: Optional[list[str]] = None,
        timeout_seconds: float = 30.0, trace_id: str = "",
    ) -> Any | None:
        if not self.enabled:
            metrics.PI_AGENT_EXECUTION.labels(agent=agent_type, status="disabled").inc()
            return None
        if not self._enter_circuit():
            metrics.PI_AGENT_EXECUTION.labels(agent=agent_type,status="circuit_open").inc()
            return None
        timeout_ms = max(250, min(int(timeout_seconds * 1000), 120_000))
        try:
            response = await self._http().post(
                f"{self.base_url}/v1/agent/run",
                headers={"X-Internal-Token": self.settings.internal_api_token},
                json={
                    "agentType": agent_type, "systemPrompt": redact(system_prompt), "prompt": redact(prompt),
                    "outputMode": output_mode, "allowedTools": allowed_tools or [],
                    "timeoutMs": timeout_ms, "traceId": trace_id,
                },
                timeout=timeout_seconds + 2.0,
            )
            response.raise_for_status()
            body = response.json()
            if body.get("code") != 0:
                self._circuit_result(False)
                metrics.PI_AGENT_EXECUTION.labels(agent=agent_type, status="error").inc()
                logger.warning("pi runtime %s 返回错误: %s", agent_type, body.get("message"))
                return None
            data = body.get("data") or {}
            if data.get("output") is None:
                raise ValueError("pi响应缺少output")
            self._circuit_result(True)
            record(agent_type,self.settings.deepseek_model,data.get("usage"),runtime="pi",latency_ms=data.get("latencyMs"))
            metrics.PI_AGENT_EXECUTION.labels(agent=agent_type, status="success").inc()
            return data.get("output")
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            self._circuit_result(False)
            metrics.PI_AGENT_EXECUTION.labels(agent=agent_type, status="fallback").inc()
            logger.warning("pi runtime %s 调用失败，回退 Python Agent: %s", agent_type, exc)
            return None

    async def run_json(self, agent_type: AgentType, system_prompt: str, prompt: str, **kwargs: Any) -> Any | None:
        return await self.run(agent_type, system_prompt, prompt, output_mode="json", **kwargs)

    async def run_text(self, agent_type: AgentType, system_prompt: str, prompt: str, **kwargs: Any) -> str | None:
        result = await self.run(agent_type, system_prompt, prompt, output_mode="text", **kwargs)
        return result if isinstance(result, str) else None


    async def stream_text(self, system_prompt, prompt, timeout_seconds=30.0):
        if not self.enabled:
            return
        async with self._http().stream("POST",f"{self.base_url}/v1/agent/stream",
            headers={"X-Internal-Token":self.settings.internal_api_token},
            json={"systemPrompt":redact(system_prompt),"prompt":redact(prompt),"timeoutMs":int(timeout_seconds*1000)},
            timeout=timeout_seconds+2) as response:
            response.raise_for_status()
            event = ""
            completed = False
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    event = line[6:].strip()
                elif line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if event == "delta":
                        yield data["delta"]
                    elif event == "result":
                        completed=True
                        record("answer",self.settings.deepseek_model,data.get("usage"),runtime="pi",latency_ms=data.get("latencyMs"))
                        metrics.PI_AGENT_EXECUTION.labels(agent="answer",status="success").inc()
                    elif event == "error":
                        raise RuntimeError(data.get("message","pi stream failed"))
            if not completed:
                raise RuntimeError("pi流式执行未收到完成帧")
