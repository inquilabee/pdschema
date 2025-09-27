from datetime import datetime

import pandas as pd
import pyarrow as pa

from pdschema.columns import Column


class Schema:
    def __init__(self, columns: list[Column]):
        self.columns = {col.name: col for col in columns}

    def __repr__(self) -> str:
        """Return a string representation of the Schema.

        Returns:
            str: A formatted string showing the schema's columns and their properties
        """
        lines = ["Schema("]
        for col in self.columns.values():
            nullable_str = "nullable=True" if col.nullable else "nullable=False"
            validators_str = f", validators={col.validators}" if col.validators else ""
            lines.append(f"    Column(name='{col.name}', dtype={col.dtype.__name__}, {nullable_str}{validators_str})")
        lines.append(")")
        return "\n".join(lines)

    def _check_missing_column(self, col_name: str, df: pd.DataFrame) -> str | None:
        return f"Missing column: {col_name}" if col_name not in df.columns else None

    def _check_nullability(self, col: Column, series: pd.Series) -> str | None:
        if not col.nullable and series.isnull().any():
            return f"Null values found in non-nullable column: {col.name}"
        return None

    def _check_type(self, col: Column, series: pd.Series) -> str | None:
        try:
            pa.array(series.dropna(), type=col.to_pyarrow_type())
        except (pa.ArrowInvalid, pa.ArrowTypeError) as e:
            return f"Type mismatch in column '{col.name}': {e}"
        return None

    def _check_validators(self, col: Column, series: pd.Series) -> list[str]:
        errors = []
        for i, val in series.items():
            if pd.isnull(val):
                continue
            for validator in col.validators:
                try:
                    if not validator(val):
                        errors.append(f"Validation failed in '{col.name}' at index {i}: {val}")
                        break
                except Exception as e:
                    errors.append(f"Validator error in '{col.name}' at index {i}: {e}")
        return errors

    def validate(self, df: pd.DataFrame) -> bool:
        errors = []

        for col_name, col in self.columns.items():
            if missing := self._check_missing_column(col_name, df):
                errors.append(missing)
                continue

            series = df[col_name]

            if nullability := self._check_nullability(col, series):
                errors.append(nullability)

            if type_error := self._check_type(col, series):
                errors.append(type_error)

            errors.extend(self._check_validators(col, series))

        if errors:
            raise ValueError("Schema validation failed:\n" + "\n".join(errors))

        return True

    @staticmethod
    def _infer_column_type(series: pd.Series) -> type:
        """Infer the Python type for a pandas Series."""
        if series.empty:
            return object

        type_checks = [
            (pd.api.types.is_integer_dtype, int),
            (pd.api.types.is_float_dtype, float),
            (pd.api.types.is_bool_dtype, bool),
            (pd.api.types.is_string_dtype, str),
            (pd.api.types.is_datetime64_dtype, datetime),
            (lambda dtype: hasattr(dtype, "categories"), str),
            (lambda series: series.apply(lambda x: isinstance(x, dict)).any(), dict),
        ]

        for check, inferred_type in type_checks:
            if callable(check) and check(series):
                return inferred_type

        # For unknown types, try to infer from the first non-null value
        sample = None if series.empty else series.dropna().iloc[0]
        return type(sample) if sample is not None else object

    @staticmethod
    def infer_schema(df: pd.DataFrame) -> "Schema":
        """Infer a Schema from a pandas DataFrame.

        This method analyzes the DataFrame's columns and their data to create
        an appropriate Schema with inferred column definitions.

        Args:
            df: The pandas DataFrame to infer the schema from

        Returns:
            Schema: A new Schema instance with inferred column definitions
        """
        columns = [
            Column(
                name=col_name,
                dtype=Schema._infer_column_type(df[col_name]),
                nullable=bool(df[col_name].isnull().any()),
            )
            for col_name in df.columns
        ]
        return Schema(columns)
