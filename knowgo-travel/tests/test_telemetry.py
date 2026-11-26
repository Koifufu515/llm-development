from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from app.core.telemetry import RequestMetrics


def test_usage_aggregation_and_request_isolation(tmp_path):
    first, second = RequestMetrics(), RequestMetrics()
    for _ in range(2):
        first.on_chat_model_start({}, [])
        first.on_llm_end(LLMResult(generations=[[ChatGeneration(message=AIMessage(
            content="secret prompt must not be logged", usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15}
        ))]]))
    result = first.save(tmp_path / "metrics.jsonl")
    assert result["llm_calls"] == 2 and result["input_tokens"] == 24
    assert result["output_tokens"] == 6 and result["usage_complete"]
    assert second.snapshot()["llm_calls"] == 0
    assert "secret prompt" not in (tmp_path / "metrics.jsonl").read_text()


def test_missing_usage_is_unknown_and_failed_call_counted():
    metrics = RequestMetrics()
    metrics.on_chat_model_start({}, [])
    metrics.on_llm_error(ValueError("private error"))
    result = metrics.snapshot("failed")
    assert result["input_tokens"] is None
    assert result["llm_errors"] == 1 and not result["usage_complete"]
