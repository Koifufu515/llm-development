#!/bin/bash
set -e
cd "$(dirname "$0")"
exec backend/.venv/bin/python scripts/local_manage.py stop
