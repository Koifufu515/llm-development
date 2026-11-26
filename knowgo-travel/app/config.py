from pathlib import Path
from urllib.parse import quote

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(PROJECT_ROOT / ".env", PROJECT_ROOT / "外部服务配置.env"), extra="ignore")

    model_provider: str = "deepseek"
    dashscope_api_key: SecretStr = SecretStr("")
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    rag_model: str = "qwen-turbo"
    tavily_api_key: SecretStr = SecretStr("")
    backup_weather_mcp_url: str = ""
    image_search_mcp_url: str = ""
    amap_api_key: SecretStr = SecretStr("")
    tencent_map_key: SecretStr = SecretStr("")
    variflight_api_key: SecretStr = SecretStr("")
    aigohotel_mcp_api: SecretStr = SecretStr("")

    deepseek_api_key: SecretStr = SecretStr("")
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-flash"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 55432
    postgres_db: str = "knowgo"
    postgres_user: str = "knowgo"
    postgres_password: SecretStr

    @property
    def database_url(self) -> str:
        user = quote(self.postgres_user, safe="")
        password = quote(self.postgres_password.get_secret_value(), safe="")
        database = quote(self.postgres_db, safe="")
        return f"postgresql://{user}:{password}@{self.postgres_host}:{self.postgres_port}/{database}"

    @property
    def model_configured(self) -> bool:
        return bool((self.dashscope_api_key if self.model_provider == "qwen" else self.deepseek_api_key).get_secret_value().strip())
