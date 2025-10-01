from copy import deepcopy

import pandas as pd
import pyarrow as pa

from pdschema.types import TYPE_MAPPINGS, infer_pyarrow_type_from_series
from pdschema.validators import Validator


class Column:
    def __init__(
        self,
        name: str | None = None,
        dtype: type | str = str,
        nullable: bool = True,
        validators: list[Validator] | None = None,
    ):
        self.name = name  # Name can be set later if not provided
        self.dtype = dtype
        self.nullable = nullable
        self.validators = validators or []

    def set_name(self, name: str):
        """Set the name of the column dynamically."""
        self.name = name

    def with_name(self, name: str):
        return self.__class__(name, self.dtype, self.nullable, deepcopy(self.validators))

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
