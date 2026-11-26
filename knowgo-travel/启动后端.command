#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")"
/opt/homebrew/bin/colima start knowgo
/opt/homebrew/bin/docker --context colima-knowgo compose up -d --wait
exec ./scripts/dev.sh
