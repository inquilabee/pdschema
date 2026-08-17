"""Validate already-cleaned frames. pdschema does not transform data."""

import pandas as pd

from pdschema import Column, IsNonEmptyString, IsPositive, Schema, Validator


class IsCleanString(Validator):
    def validate(self, value: object) -> bool:
        return isinstance(value, str) and value == value.strip() and "  " not in value


def validate_clean_frame() -> None:
    dirty = pd.DataFrame({"name": ["  John  "], "age": [25]})
    clean = pd.DataFrame({"name": ["John"], "age": [25]})
    schema = Schema(
        [
            Column("name", str, nullable=False, validators=[IsCleanString(), IsNonEmptyString()]),
            Column("age", int, nullable=False, validators=[IsPositive()]),
        ]
    )
    try:
        schema.validate(dirty)
    except ValueError as exc:
        print("Dirty frame failed validation as expected:")
        print(exc)
    schema.validate(clean)
    print("Clean frame passed validation.")


if __name__ == "__main__":
    validate_clean_frame()
