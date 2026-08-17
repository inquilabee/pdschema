install-tools:
	uvx shipgate install --suite full

format:
	uvx shipgate format --target . --full-tree

check:
	uvx shipgate check --target . --full-tree

refactor:
	uvx shipgate refactor check .

test:
	uv run pytest tests

commit:
	git add .
	pre-commit
	git status
