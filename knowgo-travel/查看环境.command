#!/usr/bin/env bash
/opt/homebrew/bin/uv --version
/opt/homebrew/bin/docker --version
/opt/homebrew/bin/docker compose version
/opt/homebrew/bin/colima status --profile knowgo
/opt/homebrew/bin/docker --context colima-knowgo info --format "Docker Server: {{.ServerVersion}} / {{.Architecture}}"
