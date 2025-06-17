import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive

df = pd.DataFrame(
    {
        "age": [25, 30, 1],
        "name": ["Alice", "Bob", "Charlie"],
        "score": [95.5, 88.0, 91.2],
    }
)

schema = Schema(
    [
        Column("age", int, nullable=False, validators=[IsPositive()]),
        Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
        Column("score", float),
    ]
)

schema.validate(df)
