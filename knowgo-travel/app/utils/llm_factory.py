from langchain_openai import ChatOpenAI

from app.config import Settings


def get_deepseek_llm(settings: Settings,*,timeout=None,max_retries=None,max_tokens=None) -> ChatOpenAI:
    if not settings.model_configured:
        raise ValueError("请先在本机 .env 配置 DEEPSEEK_API_KEY")
    if settings.model_provider == "qwen":
        return ChatOpenAI(model=settings.qwen_model,base_url=settings.qwen_base_url,
            api_key=settings.dashscope_api_key.get_secret_value().strip(),temperature=0,timeout=timeout or 60,stream_usage=True,
            max_retries=1 if max_retries is None else max_retries,max_tokens=max_tokens or 4000,extra_body={"enable_thinking":False})
    return ChatOpenAI(
        model=settings.deepseek_model,
        base_url=settings.deepseek_base_url,
        api_key=settings.deepseek_api_key.get_secret_value().strip(),
        temperature=0,
        timeout=timeout or 45,
        max_retries=1 if max_retries is None else max_retries,
        max_tokens=max_tokens or 2000,
        # 当前 DeepSeek 默认可能启用思考；需求收集先采用非思考工具调用。
        extra_body={"thinking": {"type": "disabled"}},
    )
