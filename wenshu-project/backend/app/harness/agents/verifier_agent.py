"""Verifier Agent：答案校验（引用支撑 / 与原文矛盾 / 遗漏 / 格式），不通过打回重写。"""
from __future__ import annotations

from typing import Any

from app.harness.base import Answer, VerificationResult
from app.llm.client import ChatMessage, LLMClient
from app.utils.logging import get_logger
from app.integrations.pi_runtime import PiAgentRuntimeClient

logger = get_logger(__name__)

VERIFY_PROMPT = """你是答案校验助手。检查答案是否可靠，仅输出 JSON：
{{"passed": true/false, "score": 0.0-1.0, "issues": ["问题1", "问题2"]}}

检查项：
- 明确说明现有文件未找到依据、没有补造事实的拒答应当通过；不要求额外解释文档覆盖范围。
- 仅核对当前问题直接要求的结论，不因没有回答用户未问的其它事项扣分。
- 来源编号只对应外层[来源N]标记，表格序号和文档条号不是来源编号。
1. 每个关键结论是否有条款支撑（引用来源）
2. 是否与原文矛盾
3. 是否遗漏回答当前问题所必需的关键信息；无需复述与问题无关的所有条款
4. 引用格式是否正确（编号使用[来源N]，以以下参考条款为唯一映射）

参考条款：
{chunks}

答案：
{answer}

用户问题：{query}
"""


class VerifierAgent:
    def __init__(
        self, llm: LLMClient, pi_runtime: PiAgentRuntimeClient | None = None, timeout: float = 3.0,
    ) -> None:
        self.llm = llm
        self.pi_runtime = pi_runtime
        self.timeout = timeout

    async def verify(self, query: str, answer: Answer, chunks: list[dict[str, Any]]) -> VerificationResult:
        if not chunks:
            return VerificationResult(passed=False, score=0.0, issues=["无可验证的官方证据，不能确认事实结论"])
        chunks_text = "\n\n".join(f"[来源{i+1}] {c.get('content', '')}" for i, c in enumerate(chunks))
        try:
            prompt = VERIFY_PROMPT.format(chunks=chunks_text, answer=answer.content, query=query)
            data = None
            if self.pi_runtime is not None:
                data = await self.pi_runtime.run_json(
                    "verify", "你是严谨的答案校验助手。", prompt,
                    timeout_seconds=self.timeout,
                )
            if not isinstance(data, dict):
                messages = [ChatMessage.system("你是严谨的答案校验助手。"), ChatMessage.user(prompt)]
                data = await self.llm.complete_json(messages, temperature=0.0)
            return VerificationResult.from_dict(data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("答案语义校验不可用(%s)，转原文降级", type(exc).__name__)
            return VerificationResult(False, 0.0, ["语义校验不可用，不能以引用存在代替事实支撑"])

    @staticmethod
    def _heuristic(answer: Answer, chunks: list[dict[str, Any]]) -> VerificationResult:
        issues: list[str] = []
        if not answer.citations:
            issues.append("答案缺少引用来源")
        if not answer.content.strip():
            issues.append("答案为空")
        score = 1.0 - 0.3 * len(issues)
        return VerificationResult(passed=len(issues) == 0, score=max(score, 0.0), issues=issues)
