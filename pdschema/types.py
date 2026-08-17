from collections.abc import Callable, Mapping
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import ClassVar, cast

import numpy as np
import pandas as pd
import pyarrow as pa


class TypeRegistry:
    """Internal type mapping registry."""

    PYARROW_PANDAS: ClassVar[dict[object, pa.DataType]] = {
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

    PANDAS_TO_PA: ClassVar[dict[str, pa.DataType]] = {
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
        "datetime64[ns]": pa.timestamp("us"),
        "timedelta64[ns]": pa.duration("us"),
        "category": pa.dictionary(pa.int32(), pa.string()),
    }

    PYTHON_TO_PA: ClassVar[dict[type[object], pa.DataType]] = {
        bool: pa.bool_(),
        np.bool_: pa.bool_(),
        int: pa.int64(),
        float: pa.float64(),
        str: pa.string(),
        datetime: pa.timestamp("us"),
        date: pa.date32(),
        time: pa.time64("us"),
        Decimal: pa.decimal128(38, 18),
        list: pa.list_(pa.null()),
        np.integer: pa.int64(),
        np.floating: pa.float64(),
        np.str_: pa.string(),
        np.datetime64: pa.timestamp("us"),
        np.timedelta64: pa.duration("us"),
        timedelta: pa.duration("us"),
    }

    TYPE_MAPPINGS: ClassVar[list[Mapping[object, pa.DataType]]] = [
        PYARROW_PANDAS,
        cast(Mapping[object, pa.DataType], PYTHON_TO_PA),
    ]

    PANDAS_TYPE_PREDICATES: ClassVar[list[tuple[Callable[[object], bool], pa.DataType]]] = [
        (pd.api.types.is_bool_dtype, pa.bool_()),
        (pd.api.types.is_integer_dtype, pa.int64()),
        (pd.api.types.is_float_dtype, pa.float64()),
        (pd.api.types.is_datetime64_any_dtype, pa.timestamp("us")),
        (pd.api.types.is_timedelta64_dtype, pa.duration("us")),
        (pd.api.types.is_string_dtype, pa.string()),
    ]

    @classmethod
    def infer_object_type(cls, value: object) -> pa.DataType:
        """Infer PyArrow type from a single Python object."""
        for py_type, pa_type in cls.PYTHON_TO_PA.items():
            if isinstance(value, py_type):
                return pa_type
        raise TypeError(f"Unsupported type: {type(value)}")

    @classmethod
    def infer_object_series_type(cls, s: pd.Series) -> pa.DataType:
        """Infer PyArrow type from a pandas Series with object dtype."""
        non_null_values = s.dropna()
        if non_null_values.empty:
            return pa.null()

        value_types = {type(x) for x in non_null_values}
        if len(value_types) > 1:
            raise TypeError("Cannot infer type from mixed-type object Series")

        return cls.infer_object_type(non_null_values.iloc[0])

    @classmethod
    def types_compatible(cls, expected: pa.DataType, inferred: pa.DataType, declared: object) -> bool:
        if str(expected) == str(inferred):
            return True
        if declared is int:
            return pa.types.is_signed_integer(inferred)
        if declared is float:
            return pa.types.is_floating(inferred)
        return False


def infer_pyarrow_type_from_series(s: pd.Series) -> pa.DataType:
    """Infer PyArrow type from a pandas Series."""
    if s.empty or s.isna().all():
        return pa.null()
    dtype = s.dtype
    pyarrow_dtype = getattr(dtype, "pyarrow_dtype", None)
    if pyarrow_dtype is not None:
        return pyarrow_dtype
    if isinstance(dtype, pd.DatetimeTZDtype):
        return pa.timestamp("us", tz=str(dtype.tz))
    if dtype == "object":
        return TypeRegistry.infer_object_series_type(s)
    dtype_name = str(dtype)
    if dtype_name in TypeRegistry.PANDAS_TO_PA:
        return TypeRegistry.PANDAS_TO_PA[dtype_name]
    for predicate, pa_type in TypeRegistry.PANDAS_TYPE_PREDICATES:
        if predicate(dtype):
            return pa_type
    raise TypeError(f"Unsupported dtype: {dtype}")


TYPE_MAPPINGS = TypeRegistry.TYPE_MAPPINGS
