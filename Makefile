SHIPGATE ?= uvx --python 3.13 shipgate
PROJECT_ENV ?= .venv

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

commit:
	git add .
	pre-commit
	git status
