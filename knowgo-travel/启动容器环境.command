#!/usr/bin/env bash
set -eu
/opt/homebrew/bin/colima start knowgo
/opt/homebrew/bin/docker --context colima-knowgo version
