#!/usr/bin/env bash
set -eu

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(dirname "$project_dir")"

export UV_CACHE_DIR="$workspace_dir/.tools/uv-cache"
export UV_PYTHON_INSTALL_DIR="$workspace_dir/.tools/python"
export UV_PYTHON_BIN_DIR="$workspace_dir/.tools/python-bin"

cd "$project_dir"
"$project_dir/.venv/bin/python" scripts/patch_rail_mcp.py
exec "$workspace_dir/.tools/uv/bin/uv" run --frozen uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
