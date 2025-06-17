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
    assert col.validators == []

    # Test with validators
    col = Column("age", int, nullable=False, validators=[IsPositive()])
    assert col.name == "age"
    assert col.dtype == int
    assert col.nullable is False
    assert len(col.validators) == 1
    assert isinstance(col.validators[0], IsPositive)


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
