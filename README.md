# PySchema

A Python project using Poetry for dependency management.

## Requirements

- Python 3.13
- Poetry

## Setup

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Install pre-commit hooks:
   ```bash
   poetry run pre-commit install
   ```

## Development

The project uses the following tools for code quality:

- Black for code formatting
- isort for import sorting
- Ruff for linting
- pre-commit for git hooks

To manually run the code quality tools:

```bash
# Format code
poetry run black .
poetry run isort .

# Run linter
poetry run ruff check .
```

## License

[Your chosen license]
