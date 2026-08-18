from datetime import datetime
from typing import ClassVar

import pandas as pd

from pdschema.columns import Column
from pdschema.errors import SchemaValidationError


class SchemaMeta(type):
    """Metaclass for Schema to collect declared Column fields across the MRO."""

    def __new__(cls, name, bases, dct):
        own = {key: value for key, value in dct.items() if isinstance(value, Column)}
        for key in own:
            dct.pop(key)
        columns: dict[str, Column] = {}
        for base in reversed(cls._base_mro(bases)):
            if declared := getattr(base, "_declared_columns", None):
                columns.update(declared)
        columns.update(own)
        dct["_declared_columns"] = columns
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def _c3_head(sequences: list[list[type]]) -> type:
        for seq in sequences:
            head = seq[0]
            if all(head not in other[1:] for other in sequences):
                return head
        raise TypeError("Cannot create a consistent column MRO")

    @staticmethod
    def _base_mro(bases: tuple[type, ...]) -> tuple[type, ...]:
        if not bases:
            return ()
        sequences = [list(base.__mro__) for base in bases]
        sequences.append(list(bases))
        result: list[type] = []
        while True:
            nonempty = [seq for seq in sequences if seq]
            if not nonempty:
                return tuple(result)
            candidate = SchemaMeta._c3_head(nonempty)
            result.append(candidate)
            for seq in sequences:
                if seq and seq[0] is candidate:
                    del seq[0]


class Schema(metaclass=SchemaMeta):
    _declared_columns: ClassVar[dict[str, Column]] = {}

    def __init__(self, columns: list[Column] | None = None, *, strict: bool = False):
        self.strict = strict
        if columns is None:
            self.columns = {} if not self._declared_columns else {
                col_name: col_obj.with_name(col_name) for col_name, col_obj in self._declared_columns.items()
            }
            return
        named: dict[str, Column] = {}
        for col in columns:
            if col.name is None:
                raise SchemaValidationError("Column name cannot be None")
            named[col.name] = col
        self.columns = named

    def __repr__(self) -> str:
        lines = ["Schema("]
        for col in self.columns.values():
            nullable_str = "nullable=True" if col.nullable else "nullable=False"
            validators_str = f", validators={col.validators}" if col.validators else ""
            dtype_str = col.dtype.__name__ if isinstance(col.dtype, type) else col.dtype
            lines.append(f"    Column(name='{col.name}', dtype={dtype_str}, {nullable_str}{validators_str})")
        lines.append(")")
        return "\n".join(lines)

    def validate(self, df: pd.DataFrame) -> bool:
        if errors := self._collect_errors(df):
            raise SchemaValidationError("Schema validation failed:\n" + "\n".join(errors))
        return True

    def _collect_errors(self, df: pd.DataFrame) -> list[str]:
        errors: list[str] = []
        if self.strict:
            if extra := [name for name in df.columns if name not in self.columns]:
                errors.append(f"Unexpected columns: {extra}")
        for col_name, col in self.columns.items():
            errors.extend(self._column_errors(df, col_name, col))
        return errors

    def _column_errors(self, df: pd.DataFrame, col_name: str, col: Column) -> list[str]:
        if not col_name:
            raise SchemaValidationError("Column name cannot be None")
        if missing := col.check_missing(df):
            return [missing]
        series = df[col_name]
        errors: list[str] = []
        if nullability := col.check_nullability(series):
            errors.append(nullability)
        if type_error := col.check_type(series):
            errors.append(type_error)
        errors.extend(col.validate(series))
        return errors

    @classmethod
    def _infer_column_type(cls, series: pd.Series) -> type:
        if series.empty:
            return object

        type_checks = [
            (pd.api.types.is_integer_dtype, int),
            (pd.api.types.is_float_dtype, float),
            (pd.api.types.is_bool_dtype, bool),
            (pd.api.types.is_string_dtype, str),
            (pd.api.types.is_datetime64_dtype, datetime),
            (lambda values: isinstance(values.dtype, pd.CategoricalDtype), str),
            (lambda values: values.apply(lambda x: isinstance(x, dict)).any(), dict),
        ]

        for check, inferred_type in type_checks:
            if check(series):
                return inferred_type

        samples = series.dropna()
        return object if samples.empty else type(samples.iloc[0])

    @classmethod
    def infer_schema(cls, df: pd.DataFrame) -> "Schema":
        columns = [
            Column(
                name=col_name,
                dtype=cls._infer_column_type(df[col_name]),
                nullable=df[col_name].isnull().any(),
            )
            for col_name in df.columns
        ]
        return cls(columns)
