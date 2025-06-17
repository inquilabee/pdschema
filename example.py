import pandas as pd

from pyschema.columns import Column
from pyschema.schema import Schema
from pyschema.validators import IsNonEmptyString, IsPositive

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
