# Validate a pandas DataFrame

pdschema checks that a DataFrame matches a column contract. It does not clean or transform the data.

Python 3.12 or newer. Pandas and PyArrow come in with the package.

## Try this

```bash
pip install pdschema
```

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

ok = schema.validate(df)
print(ok)
```

Same contract as class attributes. The attribute name is the column name.

```python
class People(Schema):
    idx = Column(dtype=int, nullable=False)
    name = Column(dtype=str, nullable=False, validators=[IsNonEmptyString])
    age = Column(dtype=int, nullable=False, validators=[IsPositive])
    score = Column(dtype=float, nullable=False, validators=[Range(0, 100)])

People().validate(df)
```

From a frame you already trust, infer types and nullability, then tighten validators yourself.

```python
draft = Schema.infer_schema(df)
```

Reject extra columns with `strict=True`.

```python
Schema([Column("idx", int)], strict=True).validate(df)
```

## What you should see

`validate` returns `True` when every declared column is present, types match, nulls are allowed, and validators pass.

On failure it raises `SchemaValidationError` (also a `ValueError`). The message starts with `Schema validation failed:` then one line per problem.

```text
Schema validation failed:
Unexpected columns: ['extra']
Validation failed in 'age' at index 0: -1 (IsPositive)
```

Catch `SchemaValidationError` if you want that type. Catch `ValueError` if you already do. Catch `PdSchemaError` for any pdschema failure.

A string that looks numeric is still a string. `"1"` does not pass `Column("id", int)`. `True` is not an `int` on `@pdfunction` arguments.

Built-in validators (`IsPositive`, `Range`, `Choice`, etc.) run vectorized over the whole column in C. Custom validators and callables fall back to a scalar Python loop. See [Validators](validators.md) for details.

## Next

- [Check function inputs and outputs](functions.md)
- [Use and write validators](validators.md)
