# Use and write validators

Validators run on each non-null cell after the column type check. Built-ins cover bounds, membership, and string length. Subclass `Validator` for a rule you own.

## Try this

```python
import pandas as pd

from pdschema import Choice, Column, IsNonEmptyString, Length, Range, Schema

schema = Schema(
    [
        Column("status", str, validators=[Choice(["ok", "fail"])]),
        Column("label", str, validators=[IsNonEmptyString(), Length(min_length=1, max_length=8)]),
        Column("score", float, validators=[Range(0, 100)]),
    ]
)
schema.validate(
    pd.DataFrame({"status": ["ok"], "label": ["ready"], "score": [91.0]})
)
```

You can pass a validator instance, a validator class with no required arguments, or a callable that returns a bool.

```python
from pdschema import Column, Schema, Validator


class IsCleanString(Validator):
    def validate(self, value: object) -> bool:
        return isinstance(value, str) and value == value.strip() and "  " not in value


schema = Schema([Column("name", str, validators=[IsCleanString(), lambda v: v.isalpha()])])
```

## Built-in checks

| Validator | Passes when |
| --- | --- |
| `IsPositive()` | value `> 0` |
| `IsNonEmptyString()` | non-empty after `strip` |
| `Min(n)` / `GreaterThanOrEqual(n)` | value `>= n` |
| `Max(n)` / `LessThanOrEqual(n)` | value `<= n` |
| `GreaterThan(n)` | value `> n` |
| `LessThan(n)` | value `< n` |
| `Range(lo, hi)` | `lo <= value <= hi` |
| `Choice([...])` | value is in the list |
| `Length(min_length=..., max_length=...)` | `len(value)` is in range; value is str, list, dict, or tuple |

`Length` needs at least one of `min_length` or `max_length`.

## What you should see

A failing cell looks like this:

```text
Validation failed in 'score' at index 0: 101.0 (Range)
```

The name in parentheses is the validator. For a callable it is the function name. Nulls skip validators when `nullable=True`. A null in a `nullable=False` column fails before validators run.

## Next

- [Validate a DataFrame](quickstart.md)
- [Check function inputs and outputs](functions.md)
