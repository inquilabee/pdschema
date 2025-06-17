import pandas as pd
import pytest

from pdschema.types import TYPE_MAPPINGS, infer_pyarrow_type_from_series


def test_type_mappings():
    # Test Python type mappings
    assert TYPE_MAPPINGS[1][int] is not None
    assert TYPE_MAPPINGS[1][float] is not None
    assert TYPE_MAPPINGS[1][str] is not None
    assert TYPE_MAPPINGS[1][bool] is not None

    # Test pandas dtype mappings
    assert TYPE_MAPPINGS[0][pd.Int64Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.Float64Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.StringDtype()] is not None
    assert TYPE_MAPPINGS[0][pd.BooleanDtype()] is not None

    # Test additional pandas dtypes
    assert TYPE_MAPPINGS[0][pd.Int32Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.Int16Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.Int8Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.UInt64Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.UInt32Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.UInt16Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.UInt8Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.Float32Dtype()] is not None
    assert TYPE_MAPPINGS[0][pd.DatetimeTZDtype(tz="UTC")] is not None
    assert TYPE_MAPPINGS[0][pd.CategoricalDtype()] is not None
    assert TYPE_MAPPINGS[0][pd.IntervalDtype()] is not None


def test_infer_pyarrow_type_from_series(capsys=None):
    # Test integer types
    s_int = pd.Series([1, 2, 3])
    assert str(infer_pyarrow_type_from_series(s_int)) == "int64"

    # Test float types
    s_float = pd.Series([1.1, 2.2, 3.3])
    assert str(infer_pyarrow_type_from_series(s_float)) == "double"

    # Test string types
    s_str = pd.Series(["a", "b", "c"])
    assert str(infer_pyarrow_type_from_series(s_str)) == "string"

    # Test boolean types
    s_bool = pd.Series([True, False, True])
    assert str(infer_pyarrow_type_from_series(s_bool)) == "bool"

    # Test datetime types
    s_dt = pd.Series(pd.date_range("2024-01-01", periods=3))
    assert str(infer_pyarrow_type_from_series(s_dt)) == "timestamp[us]"

    # Test categorical types
    s_cat = pd.Series(pd.Categorical(["a", "b", "c"]))
    assert "dictionary" in str(infer_pyarrow_type_from_series(s_cat))

    # Test empty series
    s_empty = pd.Series([])
    assert str(infer_pyarrow_type_from_series(s_empty)) == "null"

    # Test series with all nulls
    s_nulls = pd.Series([None, None, None])
    assert str(infer_pyarrow_type_from_series(s_nulls)) == "null"

    # Test object dtype with mixed types
    s_mixed = pd.Series([1, "a", 3.14])
    print(f"DEBUG: s_mixed dtype: {s_mixed.dtype}")
    print(f"DEBUG: s_mixed types: {[type(x) for x in s_mixed.dropna()]}")
    if capsys:
        with pytest.raises(TypeError):
            infer_pyarrow_type_from_series(s_mixed)
        captured = capsys.readouterr()
        print("Captured output:", captured.out)
    else:
        with pytest.raises(TypeError):
            infer_pyarrow_type_from_series(s_mixed)

    # Test with pandas nullable integer type
    s_nullable_int = pd.Series([1, None, 3], dtype=pd.Int64Dtype())
    assert str(infer_pyarrow_type_from_series(s_nullable_int)) == "int64"

    # Test with pandas nullable float type
    s_nullable_float = pd.Series([1.1, None, 3.3], dtype=pd.Float64Dtype())
    assert str(infer_pyarrow_type_from_series(s_nullable_float)) == "double"

    # Test with pandas nullable string type
    s_nullable_str = pd.Series(["a", None, "c"], dtype=pd.StringDtype())
    assert str(infer_pyarrow_type_from_series(s_nullable_str)) == "string"

    # Test with pandas nullable boolean type
    s_nullable_bool = pd.Series([True, None, False], dtype=pd.BooleanDtype())
    assert str(infer_pyarrow_type_from_series(s_nullable_bool)) == "bool"
