import pandas as pd
import pytest

from pyschema.columns import Column
from pyschema.schema import Schema
from pyschema.validators import IsNonEmptyString, IsPositive, Range


def test_schema_valid_data():
    df = pd.DataFrame(
        {
            "age": [25, 30, 1],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [95.5, 88.0, 91.2],
        }
    )

    schema = Schema(
        [
            Column(
                "age", int, nullable=False, validators=[IsPositive(), Range(1, 100)]
            ),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("score", float),
        ]
    )

    assert schema.validate(df) is True


def test_schema_missing_column():
    df = pd.DataFrame(
        {
            "age": [25, 30, 1],
            "score": [95.5, 88.0, 91.2],
        }
    )

    schema = Schema(
        [
            Column("age", int),
            Column("name", str),
        ]
    )

    with pytest.raises(ValueError, match="Missing column: name"):
        schema.validate(df)


def test_schema_nullability_failure():
    df = pd.DataFrame(
        {
            "age": [25, None, 1],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    schema = Schema(
        [
            Column("age", int, nullable=False),
            Column("name", str),
        ]
    )

    with pytest.raises(
        ValueError, match="Null values found in non-nullable column: age"
    ):
        schema.validate(df)


def test_schema_type_mismatch():
    df = pd.DataFrame(
        {
            "age": [25, "thirty", 1],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    schema = Schema(
        [
            Column("age", int),
            Column("name", str),
        ]
    )

    with pytest.raises(ValueError, match="Type mismatch in column 'age'"):
        schema.validate(df)


def test_schema_validator_failure():
    df = pd.DataFrame(
        {
            "age": [25, 30, -5],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    schema = Schema(
        [
            Column("age", int, validators=[IsPositive()]),
            Column("name", str),
        ]
    )

    with pytest.raises(ValueError, match="Validation failed in 'age' at index 2: -5"):
        schema.validate(df)


def test_schema_multiple_errors():
    df = pd.DataFrame(
        {
            "age": [25, None, -5],
            "score": [95.5, 88.0, "invalid"],
        }
    )

    schema = Schema(
        [
            Column("age", int, nullable=False, validators=[IsPositive()]),
            Column("name", str, nullable=False),
            Column("score", float),
        ]
    )

    with pytest.raises(ValueError) as excinfo:
        schema.validate(df)

    assert "Missing column: name" in str(excinfo.value)
    assert "Null values found in non-nullable column: age" in str(excinfo.value)
    assert "Validation failed in 'age' at index 2: -5" in str(excinfo.value)
    assert "Type mismatch in column 'score'" in str(excinfo.value)
