#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
required="3.13"
have=""
if [[ -x .venv/bin/python ]]; then
	have="$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
fi
if [[ $have != "$required" ]]; then
	uv venv .venv --python 3.13 --clear
	uv pip install --python .venv -e ".[dev]"
fi
