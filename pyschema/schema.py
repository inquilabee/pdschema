import pandas as pd
import pyarrow as pa

from pyschema.columns import Column


class Schema:
    def __init__(self, columns: list[Column]):
        self.columns = {col.name: col for col in columns}

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
