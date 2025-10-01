from datetime import datetime

import pandas as pd
import pytest

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import Choice, IsNonEmptyString, IsPositive, Length, Max, Min, Range


def test_schema_validation():
    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("age", int, validators=[IsPositive()]),
            Column("score", float, validators=[Range(0, 100)]),
        ]
    )

    # Valid DataFrame
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "score": [85.5, 92.0, 78.5],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame - missing column
    df_missing = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )
    with pytest.raises(Exception, match="Missing column: age"):
        schema.validate(df_missing)

    # Invalid DataFrame - null in non-nullable column
    df_null = pd.DataFrame(
        {
            "id": [1, None, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "score": [85.5, 92.0, 78.5],
        }
    )
    with pytest.raises(ValueError, match="Null values found in non-nullable column: id"):
        schema.validate(df_null)

    # Invalid DataFrame - validation failure
    df_invalid = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "", "Charlie"],
            "age": [25, -30, 35],
            "score": [85.5, 92.0, 178.5],
        }
    )
    with pytest.raises(ValueError) as exc_info:
        schema.validate(df_invalid)
    assert "Validation failed in 'name'" in str(exc_info.value)
    assert "Validation failed in 'age'" in str(exc_info.value)
    assert "Validation failed in 'score'" in str(exc_info.value)


def test_schema_inference():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "score": [85.5, 92.0, 78.5],
            "active": [True, False, True],
            "created_at": pd.date_range("2024-01-01", periods=3),
        }
    )

    schema = Schema.infer_schema(df)
    assert schema.validate(df) is True

    # Verify column types
    assert schema.columns["id"].dtype == int
    assert schema.columns["name"].dtype == str
    assert schema.columns["age"].dtype == int
    assert schema.columns["score"].dtype == float
    assert schema.columns["active"].dtype == bool
    assert schema.columns["created_at"].dtype == datetime


def test_validators():
    # Test Max validator
    max_validator = Max(10)
    assert max_validator(5) is True
    assert max_validator(10) is True
    assert max_validator(11) is False

    # Test Min validator
    min_validator = Min(5)
    assert min_validator(5) is True
    assert min_validator(10) is True
    assert min_validator(4) is False

    # Test Range validator
    range_validator = Range(5, 10)
    assert range_validator(5) is True
    assert range_validator(7) is True
    assert range_validator(10) is True
    assert range_validator(4) is False
    assert range_validator(11) is False

    # Test Choice validator
    choice_validator = Choice(["a", "b", "c"])
    assert choice_validator("a") is True
    assert choice_validator("b") is True
    assert choice_validator("d") is False

    # Test Length validator
    length_validator = Length(min_length=2, max_length=4)
    assert length_validator("ab") is True
    assert length_validator("abc") is True
    assert length_validator("abcd") is True
    assert length_validator("a") is False
    assert length_validator("abcde") is False
    assert length_validator([1, 2]) is True
    assert length_validator([1, 2, 3, 4]) is True
    assert length_validator([1]) is False
    assert length_validator([1, 2, 3, 4, 5]) is False

    # Test Length validator with only min_length
    min_length_validator = Length(min_length=2)
    assert min_length_validator("ab") is True
    assert min_length_validator("abc") is True
    assert min_length_validator("a") is False

    # Test Length validator with only max_length
    max_length_validator = Length(max_length=4)
    assert max_length_validator("abcd") is True
    assert max_length_validator("abc") is True
    assert max_length_validator("abcde") is False

    # Test Length validator with invalid input
    assert length_validator(123) is False  # Not a sequence type


def test_schema_repr():
    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("age", int, validators=[IsPositive()]),
        ]
    )

    # Get the actual representation
    actual_repr = repr(schema)

    # Check the structure without exact string matching
    assert "Schema(" in actual_repr
    assert "Column(name='id'" in actual_repr
    assert "dtype=int" in actual_repr
    assert "nullable=False" in actual_repr
    assert "Column(name='name'" in actual_repr
    assert "dtype=str" in actual_repr
    assert "validators=[" in actual_repr
    assert "IsNonEmptyString" in actual_repr
    assert "Column(name='age'" in actual_repr
    assert "IsPositive" in actual_repr


def test_infer_column_type():
    # Test integer type
    s_int = pd.Series([1, 2, 3])
    assert Schema._infer_column_type(s_int) is int

    # Test float type
    s_float = pd.Series([1.1, 2.2, 3.3])
    assert Schema._infer_column_type(s_float) is float

    # Test boolean type
    s_bool = pd.Series([True, False, True])
    assert Schema._infer_column_type(s_bool) is bool

    # Test string type
    s_str = pd.Series(["a", "b", "c"])
    assert Schema._infer_column_type(s_str) is str

    # Test datetime type
    s_datetime = pd.Series(pd.date_range("2023-01-01", periods=3))
    assert Schema._infer_column_type(s_datetime) is datetime

    # Test categorical type
    s_categorical = pd.Series(["a", "b", "c"], dtype="category")
    assert Schema._infer_column_type(s_categorical) is str

    # Test unknown type with sample inference
    s_object = pd.Series([{"key": "value"}, {"key": "value2"}])
    assert Schema._infer_column_type(s_object) is dict

    # Test empty series
    s_empty = pd.Series([], dtype=object)
    assert Schema._infer_column_type(s_empty) is object
