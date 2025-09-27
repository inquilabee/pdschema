from datetime import date, datetime, time, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import pyarrow as pa

pyarrow__python = {
    int: pa.int64(),
    float: pa.float64(),
    str: pa.string(),
    bool: pa.bool_(),
    datetime: pa.timestamp("us"),
    date: pa.date32(),
    time: pa.time64("us"),
    Decimal: pa.decimal128(38, 18),
    list: pa.list_(pa.null()),
}

pyarrow__pandas = {
    pd.Int64Dtype(): pa.int64(),
    pd.Int32Dtype(): pa.int32(),
    pd.Int16Dtype(): pa.int16(),
    pd.Int8Dtype(): pa.int8(),
    pd.UInt64Dtype(): pa.uint64(),
    pd.UInt32Dtype(): pa.uint32(),
    pd.UInt16Dtype(): pa.uint16(),
    pd.UInt8Dtype(): pa.uint8(),
    pd.Float64Dtype(): pa.float64(),
    pd.Float32Dtype(): pa.float32(),
    pd.StringDtype(): pa.string(),
    pd.BooleanDtype(): pa.bool_(),
    pd.DatetimeTZDtype(tz="UTC"): pa.timestamp("us", tz="UTC"),
    pd.CategoricalDtype(): pa.dictionary(pa.int32(), pa.string()),
    pd.IntervalDtype(): pa.struct([("start", pa.float64()), ("end", pa.float64())]),
}

TYPE_MAPPINGS = [
    pyarrow__pandas,
    pyarrow__python,
]

_PANDAS_TO_PA = {
    "int64": pa.int64(),
    "Int64": pa.int64(),
    "int32": pa.int32(),
    "Int32": pa.int32(),
    "int16": pa.int16(),
    "Int16": pa.int16(),
    "int8": pa.int8(),
    "Int8": pa.int8(),
    "uint64": pa.uint64(),
    "UInt64": pa.uint64(),
    "uint32": pa.uint32(),
    "UInt32": pa.uint32(),
    "uint16": pa.uint16(),
    "UInt16": pa.uint16(),
    "uint8": pa.uint8(),
    "UInt8": pa.uint8(),
    "float64": pa.float64(),
    "Float64": pa.float64(),
    "float32": pa.float32(),
    "Float32": pa.float32(),
    "bool": pa.bool_(),
    "boolean": pa.bool_(),
    "string": pa.string(),
    "object": pa.string(),  # fallback for object, but handled above
    "datetime64[ns]": pa.timestamp("us"),
    "timedelta64[ns]": pa.duration("us"),
    "category": pa.dictionary(pa.int32(), pa.string()),
}

_PYTHON_TO_PA = {
    int: pa.int64(),
    float: pa.float64(),
    bool: pa.bool_(),
    str: pa.string(),
    datetime: pa.timestamp("us"),
    date: pa.date32(),
    time: pa.time64("us"),
    Decimal: pa.decimal128(38, 18),
    list: pa.list_(pa.null()),
    np.integer: pa.int64(),
    np.floating: pa.float64(),
    np.bool_: pa.bool_(),
    np.str_: pa.string(),
    np.datetime64: pa.timestamp("us"),
    np.timedelta64: pa.duration("us"),
    timedelta: pa.duration("us"),
}

_PANDAS_TYPE_PREDICATES = [
    (pd.api.types.is_integer_dtype, pa.int64()),
    (pd.api.types.is_float_dtype, pa.float64()),
    (pd.api.types.is_bool_dtype, pa.bool_()),
    (pd.api.types.is_datetime64_any_dtype, pa.timestamp("us")),
    (pd.api.types.is_timedelta64_dtype, pa.duration("us")),
    (pd.api.types.is_string_dtype, pa.string()),
]


def _infer_object_type(value):
    """Infer PyArrow type from a single Python object."""
    for py_type, pa_type in _PYTHON_TO_PA.items():
        if isinstance(value, py_type):
            return pa_type
    raise TypeError(f"Unsupported type: {type(value)}")


def _infer_object_series_type(s: pd.Series) -> pa.DataType:
    """Infer PyArrow type from a pandas Series with object dtype."""
    non_null_values = s.dropna()
    if non_null_values.empty:
        return pa.null()

    # Check if all non-null values are of the same type
    value_types = {type(x) for x in non_null_values}
    if len(value_types) > 1:
        raise TypeError("Cannot infer type from mixed-type object Series")

    # Use the type of the first non-null value
    return _infer_object_type(non_null_values.iloc[0])


def infer_pyarrow_type_from_series(s: pd.Series) -> pa.DataType:
    """Infer PyArrow type from a pandas Series."""
    if s.empty or s.isna().all():
        return pa.null()
    if s.dtype == "object":
        return _infer_object_series_type(s)
    dtype_name = str(s.dtype)
    if dtype_name in _PANDAS_TO_PA:
        return _PANDAS_TO_PA[dtype_name]
    for predicate, pa_type in _PANDAS_TYPE_PREDICATES:
        if predicate(s.dtype):
            return pa_type
    raise TypeError(f"Unsupported dtype: {s.dtype}")
