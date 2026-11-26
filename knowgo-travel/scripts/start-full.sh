#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(dirname "$project_dir")"
cd "$project_dir"
docker_bin="$(command -v docker || true)"
if [ -z "$docker_bin" ] && [ -x /opt/homebrew/bin/docker ]; then docker_bin=/opt/homebrew/bin/docker; fi
if [ -z "$docker_bin" ]; then echo '未找到Docker，请先安装Docker/Colima。'; exit 1; fi
context="${DOCKER_CONTEXT:-colima-knowgo}"
if ! "$docker_bin" --context "$context" info >/dev/null 2>&1; then
  colima_bin="$(command -v colima || true)"
  if [ -z "$colima_bin" ] && [ -x /opt/homebrew/bin/colima ]; then colima_bin=/opt/homebrew/bin/colima; fi
  if [ -z "$colima_bin" ]; then echo 'Docker引擎未运行，请启动所配置引擎。'; exit 1; fi
  "$colima_bin" start knowgo
fi
"$docker_bin" --context "$context" compose -f compose.yaml -f compose.redis.yaml up -d --wait
uv_bin="$(command -v uv || true)"
if [ -z "$uv_bin" ] && [ -x "$workspace_dir/.tools/uv/bin/uv" ]; then uv_bin="$workspace_dir/.tools/uv/bin/uv"; fi
if [ -z "$uv_bin" ]; then echo '未找到uv，请先安装uv。'; exit 1; fi
export UV_CACHE_DIR="$workspace_dir/.tools/uv-cache"
export UV_PYTHON_INSTALL_DIR="$workspace_dir/.tools/python"
export UV_PYTHON_BIN_DIR="$workspace_dir/.tools/python-bin"
export PYTHONPATH="$project_dir"
"$uv_bin" sync --frozen
if [ ! -f infra/rail-mcp/node_modules/12306-mcp/build/index.js ]; then npm --prefix infra/rail-mcp ci --ignore-scripts; fi
"$uv_bin" run --frozen python scripts/patch_rail_mcp.py
exec "$uv_bin" run --frozen uvicorn app.main:app --host 127.0.0.1 --port "${KNOWGO_PORT:-8001}"
