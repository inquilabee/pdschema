#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
scripts/ensure-venv.sh
uvx --python 3.13 shipgate check --target . --full-tree --project-env .venv
