from collections.abc import Callable
from typing import Any

import pyarrow as pa


class Column:
    def __init__(
        self,
        name: str,
        dtype: type,
        nullable: bool = True,
        validators: list[Callable[[Any], bool]] | None = None,
    ):
        self.name = name
        self.dtype = dtype
        self.nullable = nullable
        self.validators = validators or []

    def to_pyarrow_type(self):
        # Extendable map
        type_map = {
            int: pa.int64(),
            float: pa.float64(),
            str: pa.string(),
            bool: pa.bool_(),
        }
        try:
            return type_map[self.dtype]
        except KeyError as e:
            raise TypeError(f"Unsupported dtype: {self.dtype}") from e
