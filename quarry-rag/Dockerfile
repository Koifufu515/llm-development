FROM python:3.12-slim
# uv 的官方镜像里带着可执行文件，直接拷过来；上线时把 latest 换成固定版本
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

WORKDIR /app
# 先只拷依赖清单：代码改了而依赖没变时，这一层能用缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra parse --no-install-project

COPY . .
RUN uv sync --frozen --no-dev --extra parse

EXPOSE 8000
CMD ["uv", "run", "--no-sync", "uvicorn", "quarry.api.app:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
