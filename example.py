import pandas as pd

from pyschema.columns import Column
from pyschema.schema import Schema
from pyschema.validators import is_nonempty_string, is_positive

df = pd.DataFrame(
    {
        "age": [25, 30, -1],
        "name": ["Alice", "Bob", "Charlie"],
        "score": [95.5, 88.0, 91.2],
    }
)

schema = Schema(
    [
        Column("age", int, nullable=False, validators=[is_positive]),
        Column("name", str, nullable=False, validators=[is_nonempty_string]),
        Column("score", float),
    ]
)

schema.validate(df)
