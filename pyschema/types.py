from datetime import date, datetime, time
from decimal import Decimal

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
    dict: pa.map_(pa.string(), pa.null()),
    tuple: pa.list_(pa.null()),
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


def infer_pyarrow_type_from_series(s: pd.Series) -> pa.DataType:
    """Infer the PyArrow type from a pandas Series."""
    result = pa.null()

    # Mapping of pandas dtype names to PyArrow types
    dtype_mapping = {
        "int64": pa.int64(),
        "int32": pa.int64(),
        "int16": pa.int64(),
        "int8": pa.int64(),
        "float64": pa.float64(),
        "float32": pa.float64(),
        "string": pa.string(),
        "bool": pa.bool_(),
        "datetime64[ns]": pa.timestamp("us"),
        "category": pa.dictionary(pa.int32(), pa.string()),
    }

    # Check pandas dtype name first
    if hasattr(s.dtype, "name") and s.dtype.name in dtype_mapping:
        result = dtype_mapping[s.dtype.name]
    # Check pandas type categories
    elif pd.api.types.is_integer_dtype(s.dtype):
        result = pa.int64()
    elif pd.api.types.is_float_dtype(s.dtype):
        result = pa.float64()
    elif pd.api.types.is_bool_dtype(s.dtype):
        result = pa.bool_()
    elif pd.api.types.is_string_dtype(s.dtype):
        result = pa.string()
    # Handle object dtype by checking the first non-null value
    elif s.dtype == "object":
        sample = s.dropna().iloc[0] if not s.empty else None
        if sample is not None and type(sample) in pyarrow__python:
            result = pyarrow__python[type(sample)]

    return result
