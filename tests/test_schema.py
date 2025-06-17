from datetime import datetime

import pandas as pd
import pytest

from pyschema.columns import Column
from pyschema.schema import Schema
from pyschema.validators import (
    Choice,
    IsNonEmptyString,
    IsPositive,
    Length,
    Max,
    Min,
    Range,
)


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
            Column("age", int, nullable=False, validators=[IsPositive()]),
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


def test_type_inference():
    # Test date type inference
    df = pd.DataFrame(
        {
            "date_col": pd.date_range("2024-01-01", periods=3),
        }
    )
    schema = Schema.infer_schema(df)
    assert (
        schema.columns["date_col"].dtype == datetime
    )  # Changed from date32 to datetime

    # Test integer type inference
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3],
        }
    )
    schema = Schema.infer_schema(df)
    assert schema.columns["int_col"].dtype == int

    # Test float type inference
    df = pd.DataFrame(
        {
            "float_col": [1.1, 2.2, 3.3],
        }
    )
    schema = Schema.infer_schema(df)
    assert schema.columns["float_col"].dtype == float


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


def test_schema_validation_basic():
    schema = Schema(
        [
            Column(
                "age", int, nullable=False, validators=[IsPositive(), Range(0, 120)]
            ),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("score", float, validators=[Range(0.0, 100.0)]),
        ]
    )

    # Valid DataFrame
    df = pd.DataFrame(
        {
            "age": [25, 30, 35],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [95.5, 88.0, 91.2],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame - negative age
    df_invalid = df.copy()
    df_invalid.loc[0, "age"] = -1
    with pytest.raises(ValueError, match="Validation failed in 'age'"):
        schema.validate(df_invalid)

    # Invalid DataFrame - empty name
    df_invalid = df.copy()
    df_invalid.loc[0, "name"] = ""
    with pytest.raises(ValueError, match="Validation failed in 'name'"):
        schema.validate(df_invalid)

    # Invalid DataFrame - out of range score
    df_invalid = df.copy()
    df_invalid.loc[0, "score"] = 150.0
    with pytest.raises(ValueError, match="Validation failed in 'score'"):
        schema.validate(df_invalid)


def test_schema_validation_nullability():
    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("name", str, nullable=True),
        ]
    )

    # Valid DataFrame with nulls in nullable column
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", None, "Charlie"],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame with nulls in non-nullable column
    df_invalid = df.copy()
    df_invalid.loc[0, "id"] = None
    with pytest.raises(ValueError, match="Null values found in non-nullable column"):
        schema.validate(df_invalid)


def test_schema_validation_type_mismatch():
    schema = Schema(
        [
            Column("age", int),
            Column("name", str),
            Column("score", float),
        ]
    )

    # Valid DataFrame
    df = pd.DataFrame(
        {
            "age": [25, 30, 35],
            "name": ["Alice", "Bob", "Charlie"],
            "score": [95.5, 88.0, 91.2],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame - string in int column
    df_invalid = df.copy()
    df_invalid.loc[0, "age"] = "25"
    with pytest.raises(ValueError, match="Type mismatch in column 'age'"):
        schema.validate(df_invalid)


def test_schema_validation_missing_column():
    schema = Schema(
        [
            Column("age", int),
            Column("name", str),
        ]
    )

    # Valid DataFrame
    df = pd.DataFrame(
        {
            "age": [25, 30, 35],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame - missing column
    df_invalid = df.drop(columns=["name"])
    with pytest.raises(ValueError, match="Missing column: name"):
        schema.validate(df_invalid)


def test_schema_inference():
    # Create a DataFrame with various data types
    df = pd.DataFrame(
        {
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True],
            "datetime_col": pd.date_range("2024-01-01", periods=3),
            "categorical_col": pd.Categorical(["A", "B", "C"]),
            "nullable_col": [1, None, 3],
        }
    )

    # Infer schema
    schema = Schema.infer_schema(df)

    # Verify column types
    assert schema.columns["int_col"].dtype == int
    assert schema.columns["float_col"].dtype == float
    assert schema.columns["str_col"].dtype == str
    assert schema.columns["bool_col"].dtype == bool
    assert schema.columns["datetime_col"].dtype == datetime
    assert schema.columns["categorical_col"].dtype == str
    assert (
        schema.columns["nullable_col"].dtype == float
    )  # Changed from int to float due to null handling

    # Verify nullability
    assert not schema.columns["int_col"].nullable
    assert schema.columns["nullable_col"].nullable


def test_schema_repr():
    schema = Schema(
        [
            Column("age", int, nullable=False, validators=[IsPositive()]),
            Column("name", str, nullable=True),
            Column("status", str, validators=[Choice(["active", "inactive"])]),
        ]
    )

    # Get the actual representation
    actual_repr = repr(schema)

    # Check the structure without exact string matching
    assert "Schema(" in actual_repr
    assert "Column(name='age'" in actual_repr
    assert "dtype=int" in actual_repr
    assert "nullable=False" in actual_repr
    assert "validators=[" in actual_repr
    assert "IsPositive" in actual_repr
    assert "Column(name='name'" in actual_repr
    assert "dtype=str" in actual_repr
    assert "nullable=True" in actual_repr
    assert "Column(name='status'" in actual_repr
    assert "Choice" in actual_repr


def test_schema_with_complex_validators():
    schema = Schema(
        [
            Column(
                "age",
                int,
                validators=[
                    IsPositive(),
                    Range(0, 120),
                ],
            ),
            Column(
                "name",
                str,
                validators=[
                    IsNonEmptyString(),
                    Length(min_length=2, max_length=50),
                ],
            ),
        ]
    )

    # Valid DataFrame
    df = pd.DataFrame(
        {
            "age": [25, 30, 35],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )
    assert schema.validate(df) is True

    # Invalid DataFrame - multiple validation failures
    df_invalid = df.copy()
    df_invalid.loc[0, "age"] = -1
    df_invalid.loc[1, "name"] = "A"  # Too short
    with pytest.raises(ValueError) as exc_info:
        schema.validate(df_invalid)
    assert "Validation failed in 'age'" in str(exc_info.value)
    assert "Validation failed in 'name'" in str(exc_info.value)
