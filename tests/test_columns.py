from datetime import datetime

import pandas as pd
import pytest

from pdschema.columns import Column
from pdschema.validators import IsPositive


def test_column_initialization():
    # Test basic initialization
    col = Column("age", int)
    assert col.name == "age"
    assert col.dtype == int
    assert col.nullable is True
    assert not col.validators

    # Test with validators
    col = Column("age", int, nullable=False, validators=[IsPositive])
    assert col.name == "age"
    assert col.dtype == int
    assert col.nullable is False
    assert len(col.validators) == 1
    assert isinstance(col.validators[0], IsPositive) or issubclass(col.validators[0], IsPositive)


def test_column_to_pyarrow_type():
    # Test basic type conversion
    col = Column("age", int)
    assert str(col.to_pyarrow_type()) == "int64"

    col = Column("name", str)
    assert str(col.to_pyarrow_type()) == "string"

    col = Column("score", float)
    assert str(col.to_pyarrow_type()) == "double"

    col = Column("active", bool)
    assert str(col.to_pyarrow_type()) == "bool"

    # Test unsupported type
    col = Column("data", dict)
    with pytest.raises(TypeError, match="Unsupported dtype"):
        col.to_pyarrow_type()


def test_column_infer_pyarrow_type():
    # Test type inference from series
    col = Column("age", int)
    series = pd.Series([1, 2, 3])
    assert str(col.infer_pyarrow_type(series)) == "int64"

    col = Column("name", str)
    series = pd.Series(["a", "b", "c"])
    assert str(col.infer_pyarrow_type(series)) == "string"

    # Test with invalid series
    col = Column("age", int)
    series = pd.Series(["a", "b", "c"])
    with pytest.raises(TypeError, match="Unsupported dtype"):
        col.infer_pyarrow_type(series)


def test_check_type_rejects_coercible_strings():
    col = Column("age", int)
    error = col.check_type(pd.Series(["1", "2", "3"]))
    assert error is not None
    assert "expected" in error


def test_check_type_accepts_int32_for_python_int():
    col = Column("age", int)
    assert col.check_type(pd.Series([1, 2, 3], dtype="int32")) is None


def test_column_string_pandas_dtype_name():
    col = Column("age", "int64")
    assert str(col.to_pyarrow_type()) == "int64"
    assert col.check_type(pd.Series([1, 2, 3], dtype="int64")) is None


def test_column_accepts_numpy_dtype_object():
    series = pd.Series([1, 2, 3], dtype="int64")
    col = Column("age", series.dtype)
    assert col.check_type(series) is None


def test_arrow_dtype_preserves_width():
    int32_series = pd.Series([1, 2, 3], dtype="int32[pyarrow]")
    assert Column("c", "int32").check_type(int32_series) is None
    assert Column("c", "int64").check_type(int32_series) is not None
    float32_series = pd.Series([1.0, 2.0], dtype="float32[pyarrow]")
    assert Column("c", "float32").check_type(float32_series) is None


def test_naive_datetime_rejects_timezone_series():
    series = pd.Series(pd.date_range("2024-01-01", periods=2, tz="UTC"))
    error = Column("t", datetime).check_type(series)
    assert error is not None
