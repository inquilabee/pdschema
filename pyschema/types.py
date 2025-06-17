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
    pd.DatetimeTZDtype(): pa.timestamp("us"),
    pd.CategoricalDtype(): pa.dictionary(pa.int32(), pa.string()),
    pd.IntervalDtype(): pa.struct([("start", pa.float64()), ("end", pa.float64())]),
    pd.PeriodDtype(): pa.int64(),
    pd.SparseDtype(): pa.null(),
}


def get_pyarrow_type_from_series(s: pd.Series) -> pa.DataType:
    """Infer the PyArrow type from a pandas Series."""
    if s.dtype in pyarrow__pandas:
        return pyarrow__pandas[s.dtype]
    elif s.dtype == "object":
        # Try to infer the type from the first non-null value
        sample = s.dropna().iloc[0] if not s.empty else None
        if sample is not None:
            sample_type = type(sample)
            if sample_type in pyarrow__python:
                return pyarrow__python[sample_type]
    return pa.null()
