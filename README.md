# pdschema

A Python library for validating pandas DataFrames using schemas, with support for type checking, custom validators, and function input/output validation.

## Features

- Define schemas for pandas DataFrames with type checking and validation
- Support for custom validators (e.g., IsPositive, IsNonEmptyString, Range, etc.)
- Function decorator for validating input and output DataFrames
- PyArrow type integration for efficient type checking
- Schema inference from existing DataFrames
- Nullable column support
- Comprehensive type mapping between Python, pandas, and PyArrow types

## Installation

### Using pip

```bash
pip install pdschema
```

### Using Poetry

```bash
poetry add pdschema
```

## Quick Start

```python
import pandas as pd
from pdschema import Schema, Column, IsPositive, IsNonEmptyString

# Define a schema
schema = Schema([
    Column("id", int, nullable=False),
    Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
    Column("age", int, validators=[IsPositive()]),
    Column("score", float, validators=[Range(0, 100)])
])

# Create a DataFrame
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "score": [85.5, 92.0, 78.5]
})

# Validate the DataFrame
schema.validate(df)  # Raises ValueError if validation fails
```

## Function Validation

Use the `@pdfunction` decorator to validate function inputs and outputs:

```python
from pdschema import pdfunction

@pdfunction(
    arguments={
        "df": Schema([Column("id", int), Column("value", float)]),
        "threshold": float
    },
    outputs={
        "result": Schema([Column("id", int), Column("filtered_value", float)])
    }
)
def filter_values(df, threshold):
    result = df[df["value"] > threshold]
    return {"result": result}
```

## Available Validators

- `IsPositive`: Ensures numeric values are positive
- `IsNonEmptyString`: Ensures strings are non-empty
- `Max`: Ensures values are less than or equal to a maximum
- `Min`: Ensures values are greater than or equal to a minimum
- `GreaterThan`: Ensures values are greater than a threshold
- `GreaterThanOrEqual`: Ensures values are greater than or equal to a threshold
- `LessThan`: Ensures values are less than a threshold
- `LessThanOrEqual`: Ensures values are less than or equal to a threshold
- `Choice`: Ensures values are in a list of allowed choices
- `Length`: Ensures values have a specific length or length range
- `Range`: Ensures values are within a range

## Schema Inference

You can infer a schema from an existing DataFrame:

```python
df = pd.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
})

schema = Schema.infer_schema(df)
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Install development dependencies: `poetry install --with dev`
4. Make your changes
5. Run tests: `poetry run pytest`
6. Run linting: `poetry run ruff check . && poetry run ruff format .`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
