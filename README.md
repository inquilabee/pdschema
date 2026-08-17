# pdschema

Validate pandas DataFrames against column contracts. Types, nullability, and per-cell checks. No cleaning or transforms.

Python 3.12+.

```bash
pip install pdschema
```

## Quick example

```python
import pandas as pd

from pdschema import Column, IsNonEmptyString, IsPositive, Range, Schema

df = pd.DataFrame(
    {
        "idx": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 30, 35],
        "score": [85.5, 92.0, 78.5],
    }
)

schema = Schema(
    [
        Column("idx", int, nullable=False),
        Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
        Column("age", int, validators=[IsPositive()]),
        Column("score", float, validators=[Range(0, 100)]),
    ]
)

schema.validate(df)
```

## Features

**Two ways to define schemas** — pass a list of `Column` objects, or declare them as class attributes:

```python
class People(Schema):
    idx = Column(dtype=int, nullable=False)
    name = Column(dtype=str, nullable=False, validators=[IsNonEmptyString])
    age = Column(dtype=int, validators=[IsPositive])
    score = Column(dtype=float, validators=[Range(0, 100)])
```

**Schema inference** — start from a trusted DataFrame and tighten from there:

```python
draft = Schema.infer_schema(df)
```

**Strict mode** — reject DataFrames with columns not in the schema:

```python
Schema([Column("idx", int)], strict=True).validate(df)
```

**Built-in validators** — `IsNonEmptyString`, `IsPositive`, `Range`, `Min`, `Max`, `GreaterThan`, `LessThan`, `Choice`, `Length`, and more. All validators are extensible via the `Validator` abstract base class.

**`@pdfunction` decorator** — validate DataFrame inputs and outputs at function boundaries:

```python
@pdfunction(arguments={"df": schema}, outputs={"result": output_schema})
def transform(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    ...
```

**Clear error reporting** — `SchemaValidationError` (also a `ValueError`) with one line per problem:

```text
Schema validation failed:
Unexpected columns: ['extra']
Validation failed in 'age' at index 0: -1 (IsPositive)
```

Full walkthrough: [docs/user/quickstart.md](docs/user/quickstart.md).

MIT. See LICENSE.
