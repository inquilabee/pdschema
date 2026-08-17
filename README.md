# pdschema

Validate pandas DataFrames against column contracts. Types, nullability, and per-cell checks. No cleaning or transforms.

Python 3.12+.

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

schema.validate(df)
```

Full walkthrough, `@pdfunction`, and validators: [docs/user/quickstart.md](docs/user/quickstart.md).

MIT. See LICENSE.
