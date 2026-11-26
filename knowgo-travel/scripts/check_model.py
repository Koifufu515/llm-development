"""在项目目录执行 uv run python -m scripts.check_model；只输出连通结果，不打印密钥。"""
import asyncio
from app.config import Settings
from app.utils.llm_factory import get_deepseek_llm


async def main():
    settings = Settings()
    if not settings.model_configured:
        print("尚未配置：请在本机 .env 填写 DEEPSEEK_API_KEY")
        raise SystemExit(2)
    try:
        reply = await get_deepseek_llm(settings).ainvoke("请只回复：知行连接成功")
    except Exception as exc:
        print(f"模型连通未通过（{type(exc).__name__}），请检查密钥、余额与网络；未打印凭证。")
        raise SystemExit(1) from None
    print(f"真实模型调用成功：{settings.deepseek_model}")
    print(reply.content)


if __name__ == "__main__":
    asyncio.run(main())
