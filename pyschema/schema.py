from datetime import datetime

import pandas as pd
import pyarrow as pa

from pyschema.columns import Column


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
            lines.append(
                f"    Column(name='{col.name}', dtype={col.dtype.__name__}, {nullable_str}{validators_str})"  # noqa: E501
            )
        lines.append(")")
        return "\n".join(lines)

    def _check_missing_column(self, col_name: str, df: pd.DataFrame) -> str | None:
        if col_name not in df.columns:
            return f"Missing column: {col_name}"
        return None

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
                        errors.append(
                            f"Validation failed in '{col.name}' at index {i}: {val}"
                        )
                        break
                except Exception as e:
                    errors.append(f"Validator error in '{col.name}' at index {i}: {e}")
        return errors

    def validate(self, df: pd.DataFrame) -> bool:
        errors = []

        for col_name, col in self.columns.items():
            missing = self._check_missing_column(col_name, df)
            if missing:
                errors.append(missing)
                continue

            series = df[col_name]

            nullability = self._check_nullability(col, series)
            if nullability:
                errors.append(nullability)

            type_error = self._check_type(col, series)
            if type_error:
                errors.append(type_error)

            errors.extend(self._check_validators(col, series))

        if errors:
            raise ValueError("Schema validation failed:\n" + "\n".join(errors))

        return True

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
        columns = []
        for col_name in df.columns:
            series = df[col_name]
            # Infer nullability
            nullable = series.isnull().any()

            # Convert pandas dtype to Python type
            if pd.api.types.is_integer_dtype(series.dtype):
                dtype = int
            elif pd.api.types.is_float_dtype(series.dtype):
                dtype = float
            elif pd.api.types.is_bool_dtype(series.dtype):
                dtype = bool
            elif pd.api.types.is_string_dtype(series.dtype):
                dtype = str
            elif pd.api.types.is_datetime64_dtype(series.dtype):
                dtype = datetime
            elif hasattr(series.dtype, "categories"):  # Check for categorical data
                dtype = str  # Categorical data is treated as strings
            else:
                # For unknown types, try to infer from the first non-null value
                sample = series.dropna().iloc[0] if not series.empty else None
                dtype = type(sample) if sample is not None else object

            # Create column definition
            column = Column(
                name=col_name,
                dtype=dtype,
                nullable=nullable,
            )
            columns.append(column)

        return Schema(columns)
