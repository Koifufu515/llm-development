"""每个请求独立计量；仅保存计数，不保存提示词、模型回答或凭证。"""
import json
import logging
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("knowgo.metrics")


class RequestMetrics(BaseCallbackHandler):
    def __init__(self):
        self.request_id = str(uuid4())
        self.started = perf_counter()
        self.calls = 0
        self.errors = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.usage_calls = 0
        self.first_token_seconds = None

    def on_chat_model_start(self, serialized, messages, **kwargs):
        self.calls += 1

    def on_llm_new_token(self, token, **kwargs):
        if token and self.first_token_seconds is None:self.first_token_seconds=round(perf_counter()-self.started,4)

    def on_llm_end(self, response, **kwargs):
        # LangChain ChatGeneration 的标准 usage_metadata；缺失时保持未知。
        for generations in response.generations:
            if not generations:
                continue
            usage = getattr(getattr(generations[0], "message", None), "usage_metadata", None)
            if usage:
                self.usage_calls += 1
                self.input_tokens += usage.get("input_tokens", 0)
                self.output_tokens += usage.get("output_tokens", 0)

    def on_llm_error(self, error, **kwargs):
        self.errors += 1

    def snapshot(self, status="ok"):
        return {
            "request_id": self.request_id, "status": status,
            "elapsed_seconds": round(perf_counter() - self.started, 4),
            "llm_calls": self.calls, "llm_errors": self.errors,
            "usage_reported_calls": self.usage_calls,
            "input_tokens": self.input_tokens if self.usage_calls or self.calls==0 else None,
            "output_tokens": self.output_tokens if self.usage_calls or self.calls==0 else None,
            "usage_complete": self.usage_calls == self.calls,
            "first_token_seconds": self.first_token_seconds,
        }

    def save(self, path: Path, status="ok"):
        result = self.snapshot(status)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(result, ensure_ascii=False) + "\n")
        except OSError:
            logger.warning("Unable to save request metrics")
        return result
