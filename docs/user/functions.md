# Check function inputs and outputs

`@pdfunction` validates named arguments and a dict of outputs before the caller sees the return value.

## Try this

```python
import pandas as pd

from pdschema import Column, Schema, pdfunction

row = Schema([Column("id", int), Column("value", float)])
out = Schema([Column("id", int), Column("filtered_value", float)])


@pdfunction(
    arguments={"df": row, "threshold": float},
    outputs={"result": out},
)
def filter_values(df, threshold):
    result = df[df["value"] > threshold].rename(columns={"value": "filtered_value"})
    return {"result": result}


frame = pd.DataFrame({"id": [1, 2], "value": [10.0, 3.0]})
print(filter_values(frame, 5.0))
print(filter_values(df=frame, threshold=5.0))
```

Every name in `arguments` is checked for both positional and keyword calls. Names must match the function signature.

If you declare `outputs`, return a dict whose keys match those names. A Schema value must be a DataFrame. A type value is checked with `isinstance` (`bool` is not `int`).

You can pass a Schema class instead of an instance.

```python
class Row(Schema):
    id = Column(dtype=int)
    value = Column(dtype=float)


@pdfunction(arguments={"df": Row})
def count_rows(df):
    return len(df)
```

## What you should see

A matching call runs the function and returns whatever the function returned.

A contract miss raises `FunctionSchemaError` (also a `TypeError`). Typical messages:

```text
Declared outputs require a dict return value
Missing output: result
Argument 'df' must be a pandas DataFrame
Argument 'threshold' must be of type <class 'float'>
unknown argument 'typo'
```

A DataFrame that fails the Schema still raises `SchemaValidationError` from `validate`, same as a direct schema check.

## Next

- [Validate a DataFrame](quickstart.md)
- [Use and write validators](validators.md)
