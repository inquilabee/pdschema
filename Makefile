SHIPGATE ?= uvx --python 3.13 shipgate
PROJECT_ENV ?= .venv

setup:
	scripts/ensure-venv.sh
	$(SHIPGATE) install --suite full

install-tools:
	$(SHIPGATE) install --suite full

format:
	$(SHIPGATE) format --target . --full-tree --project-env $(PROJECT_ENV)

check:
	$(SHIPGATE) check --target . --full-tree --project-env $(PROJECT_ENV)

refactor:
	$(SHIPGATE) refactor check .

test:
	uv run --python $(PROJECT_ENV) pytest tests

hooks:
	pre-commit run --all-files
