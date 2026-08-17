import pandas as pd
import pytest

from pdschema import Column, Schema, Validator
from pdschema.validators import (
    Choice,
    IsNonEmptyString,
    IsPositive,
    Length,
    Max,
    Min,
    Range,
)


def test_vectorized_all_builtin_validators():
    schema = Schema(
        [
            Column("id", int, nullable=False, validators=[IsPositive()]),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("age", int, nullable=False, validators=[Range(0, 120)]),
            Column("score", float, nullable=False, validators=[Min(0), Max(100)]),
            Column("label", str, nullable=False, validators=[Choice(["a", "b", "c"])]),
        ]
    )
    df_pass = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "score": [85.5, 92.0, 78.5],
            "label": ["a", "b", "c"],
        }
    )
    assert schema.validate(df_pass) is True


MIN_LEN = 3


def test_vectorized_error_messages_match_scalar():
    class CustomValidator(Validator):
        def validate(self, value: object) -> bool:
            return isinstance(value, str) and len(value) > MIN_LEN

        def __str__(self) -> str:
            return "CustomValidator"

    vec_schema = Schema([Column("x", str, validators=[IsNonEmptyString()])])
    scalar_schema = Schema([Column("x", str, validators=[CustomValidator()])])

    df = pd.DataFrame({"x": ["", "ab", "hello"]})

    with pytest.raises(ValueError) as vec_exc:
        vec_schema.validate(df)
    with pytest.raises(ValueError) as scalar_exc:
        scalar_schema.validate(df)

    assert "Validation failed in 'x' at index 0" in str(vec_exc.value)
    assert "Validation failed in 'x' at index 0" in str(scalar_exc.value)


def test_mixed_vectorized_and_scalar():
    class CustomCheck(Validator):
        def validate(self, value: object) -> bool:
            return isinstance(value, str) and value.startswith("x")

        def __str__(self) -> str:
            return "CustomCheck"

    schema = Schema(
        [
            Column("name", str, validators=[IsNonEmptyString(), CustomCheck()]),
        ]
    )

    df_pass = pd.DataFrame({"name": ["xenia", "xander"]})
    assert schema.validate(df_pass) is True

    df_fail_vec = pd.DataFrame({"name": ["", "xander"]})
    with pytest.raises(ValueError, match="Validation failed in 'name' at index 0"):
        schema.validate(df_fail_vec)

    df_fail_scalar = pd.DataFrame({"name": ["alice", "xander"]})
    with pytest.raises(ValueError, match="Validation failed in 'name' at index 0"):
        schema.validate(df_fail_scalar)


def test_vectorized_empty_series():
    schema = Schema([Column("x", int, validators=[IsPositive()])])
    df = pd.DataFrame({"x": pd.Series([], dtype=int)})
    assert schema.validate(df) is True


def test_vectorized_all_null_nullable():
    schema = Schema([Column("x", int, nullable=True, validators=[IsPositive()])])
    df = pd.DataFrame({"x": pd.Series([None, None, None], dtype=object)})
    assert schema.validate(df) is True


def test_vectorized_partial_null():
    schema = Schema([Column("x", int, nullable=True, validators=[IsPositive()])])
    df = pd.DataFrame({"x": [1, None, -1]})
    with pytest.raises(ValueError, match="Validation failed in 'x' at index 2"):
        schema.validate(df)


def test_vectorized_length_validator():
    schema = Schema([Column("name", str, validators=[Length(min_length=2, max_length=5)])])
    df_pass = pd.DataFrame({"name": ["ab", "abc", "abcd", "abcde"]})
    assert schema.validate(df_pass) is True

    df_fail = pd.DataFrame({"name": ["a", "abcdef"]})
    with pytest.raises(ValueError) as exc:
        schema.validate(df_fail)
    assert "Validation failed in 'name' at index 0" in str(exc.value)
    assert "Validation failed in 'name' at index 1" in str(exc.value)


def test_validate_vector_returns_mask():
    v = IsPositive()
    series = pd.Series([1, -1, 2, 0])
    mask = v.validate_vector(series)
    assert mask.tolist() == [True, False, True, False]

    v2 = Range(0, 10)
    mask2 = v2.validate_vector(series)
    assert mask2.tolist() == [True, False, True, True]

    v3 = Choice(["a", "b"])
    mask3 = v3.validate_vector(pd.Series(["a", "c", "b"]))
    assert mask3.tolist() == [True, False, True]


def test_callable_validator_stays_scalar():
    schema = Schema([Column("x", int, validators=[lambda v: v > 0])])
    df = pd.DataFrame({"x": [1, -1, 2]})
    with pytest.raises(ValueError, match="Validation failed in 'x' at index 1"):
        schema.validate(df)
