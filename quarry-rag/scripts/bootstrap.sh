#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
quarry_context="${QUARRY_DOCKER_CONTEXT:-$(docker context show)}"
quarry_project="${COMPOSE_PROJECT_NAME:-quarry-rag}"
quarry_uv="${QUARRY_UV:-uv}"
if [ ! -f .env ]; then
  printf '%s\n' '请先复制.env.example为.env并在本机填写数据库密码和模型Key。'
  exit 2
fi
"$quarry_uv" sync --frozen --extra parse --extra dev
"$quarry_uv" run --no-sync python - <<'PY'
from pathlib import Path
import re
s=Path('.env').read_text()
for key,value in {'POSTGRES_HOST':'postgres','POSTGRES_PORT':'5432','REDIS_HOST':'redis','REDIS_PORT':'6379','APP_ENV':'production'}.items():
    s=re.sub(rf'(?m)^{key}=.*$',f'{key}={value}',s)
p=Path('.env.docker');p.write_text(s);p.chmod(0o600)
PY
docker --context "$quarry_context" compose -p "$quarry_project" pull postgres redis
docker --context "$quarry_context" volume create "${quarry_project}_init_sql" >/dev/null
docker --context "$quarry_context" run --rm -i --entrypoint sh --mount "type=volume,src=${quarry_project}_init_sql,dst=/init" pgvector/pgvector:0.8.6-pg17 -c 'cat > /init/10-init.sql' < docker/init-db.sql
# 镜像构建代理按需从环境传入，不把代理或密钥写进镜像。
docker --context "$quarry_context" compose -p "$quarry_project" build --build-arg HTTP_PROXY="${QUARRY_HTTP_PROXY:-}" --build-arg HTTPS_PROXY="${QUARRY_HTTP_PROXY:-}" api
docker --context "$quarry_context" volume create "${quarry_project}_corpusdata" >/dev/null
COPYFILE_DISABLE=1 tar --no-xattrs --exclude='._*' -C corpus -cf - . | docker --context "$quarry_context" run --rm -i --entrypoint tar --mount "type=volume,src=${quarry_project}_corpusdata,dst=/app/corpus" quarry-rag:local --skip-old-files -xf - -C /app/corpus
docker --context "$quarry_context" compose -p "$quarry_project" up -d --wait postgres redis
docker --context "$quarry_context" compose -p "$quarry_project" run --rm --no-deps api uv run --no-sync alembic upgrade head
docker --context "$quarry_context" compose -p "$quarry_project" run --rm --no-deps api uv run --no-sync python -m quarry.scripts.prepare_demo
docker --context "$quarry_context" compose -p "$quarry_project" --profile dev up -d --wait --no-deps api devapi worker
printf '%s\n' '生产API: http://127.0.0.1:8113；开发调试台: http://127.0.0.1:8110/web/debug.html'
