#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
if [[ ! -x .venv/bin/python ]]; then
  uv venv .venv --python 3.13
  uv pip install --python .venv -e ".[dev]"
fi
