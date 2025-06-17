# PySchema

A Python library for schema validation and type inference of pandas DataFrames using PyArrow types.

## Features

- Schema validation for pandas DataFrames
- Type inference from pandas Series to PyArrow types
- Rich set of built-in validators
- Support for both Python types and pandas dtypes
- Nullability checks
- Custom validator support

## Installation

```bash
pip install pyschema
```

## Quick Start

```python
import pandas as pd
from pyschema import Schema, Column
from pyschema.validators import IsPositive, IsNonEmptyString, Range

# Define your schema
schema = Schema([
    Column("age", int, nullable=False, validators=[IsPositive(), Range(0, 120)]),
    Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
    Column("score", float, validators=[Range(0.0, 100.0)]),
])

# Create a DataFrame
df = pd.DataFrame({
    "age": [25, 30, 35],
    "name": ["Alice", "Bob", "Charlie"],
    "score": [95.5, 88.0, 91.2],
})

# Validate the DataFrame
schema.validate(df)  # Returns True if valid, raises ValueError if invalid
```

## Built-in Validators

PySchema provides a rich set of built-in validators:

```python
from pyschema.validators import (
    IsPositive,
    IsNonEmptyString,
    Max,
    Min,
    Range,
    GreaterThan,
    LessThan,
    Choice,
    Length,
)

# Examples
Column("age", int, validators=[IsPositive(), Max(120)])
Column("score", float, validators=[Range(0.0, 100.0)])
Column("status", str, validators=[Choice(["active", "inactive", "pending"])])
Column("description", str, validators=[Length(min_length=10, max_length=500)])
```

## Type Support

PySchema supports both Python types and pandas dtypes, mapping them to appropriate PyArrow types:

### Python Types
- `int` → `pa.int64()`
- `float` → `pa.float64()`
- `str` → `pa.string()`
- `bool` → `pa.bool_()`
- `datetime` → `pa.timestamp("us")`
- `date` → `pa.date32()`
- `time` → `pa.time64("us")`
- `Decimal` → `pa.decimal128(38, 18)`

### Pandas Dtypes
- `Int64Dtype` → `pa.int64()`
- `Float64Dtype` → `pa.float64()`
- `StringDtype` → `pa.string()`
- `BooleanDtype` → `pa.bool_()`
- `DatetimeTZDtype` → `pa.timestamp("us")`
- `CategoricalDtype` → `pa.dictionary(pa.int32(), pa.string())`

## API Reference

### Schema

```python
class Schema:
    def __init__(self, columns: list[Column]):
        """Initialize a schema with a list of columns."""
        pass

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate a DataFrame against the schema.

        Returns:
            bool: True if valid

        Raises:
            ValueError: If validation fails, with detailed error messages
        """
        pass
```

### Column

```python
class Column:
    def __init__(
        self,
        name: str,
        dtype: type,
        nullable: bool = True,
        validators: list[Validator] | None = None,
    ):
        """Initialize a column definition.

        Args:
            name: Column name
            dtype: Python type or pandas dtype
            nullable: Whether the column can contain null values
            validators: List of validators to apply
        """
        pass
```

### Validators

All validators inherit from the `Validator` abstract base class and implement the `validate` method:

```python
class Validator(ABC):
    @abstractmethod
    def validate(self, value) -> bool:
        """Return True if value is valid, else False."""
        pass
```

## Development

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

4. Run tests:
   ```bash
   poetry run pytest
   ```

## License

[Your chosen license]
