import pandas as pd
import pyarrow as pa

from pdschema.types import TYPE_MAPPINGS, infer_pyarrow_type_from_series
from pdschema.validators import Validator


class Column:
    def __init__(
        self,
        name: str,
        dtype: type,
        nullable: bool = True,
        validators: list[Validator] | None = None,
    ):
        self.name = name
        self.dtype = dtype
        self.nullable = nullable
        self.validators = validators or []

    def to_pyarrow_type(self):
        for mapping in TYPE_MAPPINGS:
            if self.dtype in mapping:
                return mapping[self.dtype]

        raise TypeError(f"Unsupported dtype: {self.dtype}")

    def infer_pyarrow_type(self, values: pd.Series):
        try:
            inferred = infer_pyarrow_type_from_series(values)
            if inferred == pa.null():
                raise TypeError("Unsupported dtype")
            # Check if the inferred type matches the column's expected type
            expected_type = self.to_pyarrow_type()
            if str(inferred) != str(expected_type):
                raise TypeError("Unsupported dtype")
            return inferred
        except Exception as err:
            raise TypeError("Unsupported dtype") from err
