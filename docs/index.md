---
hide:
  - navigation
---

<div class="pd-hero" markdown="0">

# pdschema

Validate pandas DataFrames against column contracts.
Types, nullability, and per-cell checks — no cleaning or transforms.

</div>

<div class="pd-cards" markdown="0">

<div class="pd-card" markdown="0">

#### Column Contracts

Declare dtype, nullability, and per-column validators in a `Schema`.

</div>

<div class="pd-card" markdown="0">

#### Class-Based Schemas

Define columns as class attributes — inherit, compose, reuse.

</div>

<div class="pd-card" markdown="0">

#### Function Validation

`@pdfunction` checks DataFrame inputs and outputs at call time.

</div>

<div class="pd-card" markdown="0">

#### Extensible Validators

Subclass `Validator` or pass any `callable` that returns a bool.

</div>

</div>

## Try it

```bash
pip install pdschema
```

```python
import pandas as pd

from pdschema import Column, IsNonEmptyString, IsPositive, Range, Schema

df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "score": [85.5, 92.0, 78.5],
})

schema = Schema([
    Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
    Column("age", int, validators=[IsPositive()]),
    Column("score", float, validators=[Range(0, 100)]),
])

schema.validate(df)
```

## Guides

| Guide | What you learn |
| --- | --- |
| [Quickstart](user/quickstart.md) | Define a schema, validate a DataFrame, read errors |
| [Validators](user/validators.md) | Built-in checks and writing your own |
| [Functions](user/functions.md) | Validate inputs and outputs with `@pdfunction` |
