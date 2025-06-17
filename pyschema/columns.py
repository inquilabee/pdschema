import contextlib

import pandas as pd

from pyschema.types import TYPE_MAPPINGS, infer_pyarrow_type_from_series
from pyschema.validators import Validator


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
        with contextlib.suppress(Exception):
            return infer_pyarrow_type_from_series(values)

        raise TypeError(f"Unsupported dtype: {self.dtype}")
