from datetime import datetime
from typing import ClassVar

import pandas as pd

from pdschema.columns import Column


class SchemaMeta(type):
    """Metaclass for Schema to collect declared Column fields across the MRO."""

    def __new__(cls, name, bases, dct):
        columns: dict[str, Column] = {}
        for base in bases:
            declared = getattr(base, "_declared_columns", None)
            if declared:
                columns.update(declared)
        own = {key: value for key, value in dct.items() if isinstance(value, Column)}
        for key in own:
            dct.pop(key)
        columns.update(own)
        dct["_declared_columns"] = columns
        return super().__new__(cls, name, bases, dct)


class Schema(metaclass=SchemaMeta):
    _declared_columns: ClassVar[dict[str, Column]] = {}

    def __init__(self, columns: list[Column] | None = None, *, strict: bool = False):
        self.strict = strict
        if not columns and not self._declared_columns:
            self.columns = {}
        elif columns:
            self.columns = {col.name: col for col in columns}
        else:
            self.columns = {
                col_name: col_obj.with_name(col_name) for col_name, col_obj in self._declared_columns.items()
            }

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
        errors = []

        if self.strict:
            extra = [name for name in df.columns if name not in self.columns]
            if extra:
                errors.append(f"Unexpected columns: {extra}")

        for col_name, col in self.columns.items():
            if not col_name:
                raise ValueError("Column name cannot be None")

            if missing := col.check_missing(df):
                errors.append(missing)
                continue

            series = df[col_name]

            if nullability := col.check_nullability(series):
                errors.append(nullability)

            if type_error := col.check_type(series):
                errors.append(type_error)

            errors.extend(col.validate(series))

        if errors:
            raise ValueError("Schema validation failed:\n" + "\n".join(errors))

        return True

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

        sample = None if series.empty else series.dropna().iloc[0]
        return type(sample) if sample is not None else object

    @classmethod
    def infer_schema(cls, df: pd.DataFrame) -> "Schema":
        columns = [
            Column(
                name=col_name,
                dtype=cls._infer_column_type(df[col_name]),
                nullable=bool(df[col_name].isnull().any()),
            )
            for col_name in df.columns
        ]
        return cls(columns)
