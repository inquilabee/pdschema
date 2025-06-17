from pyschema.types import pyarrow__python
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
        try:
            return pyarrow__python[self.dtype]
        except KeyError as e:
            raise TypeError(f"Unsupported dtype: {self.dtype}") from e
