import pandas as pd
import pyarrow as pa

from pyschema.columns import Column


class Schema:
    def __init__(self, columns: list[Column]):
        self.columns = {col.name: col for col in columns}

    def validate(self, df: pd.DataFrame) -> bool:
        errors = []

        for col_name, col in self.columns.items():
            if col_name not in df.columns:
                errors.append(f"Missing column: {col_name}")
                continue

            series = df[col_name]

            # Nullability
            if not col.nullable and series.isnull().any():
                errors.append(f"Null values found in non-nullable column: {col_name}")

            # Type check with pyarrow
            try:
                pa.array(series.dropna(), type=col.to_pyarrow_type())
            except (pa.ArrowInvalid, pa.ArrowTypeError) as e:
                errors.append(f"Type mismatch in column '{col_name}': {e}")

            # Custom validators
            for i, val in series.items():
                if pd.isnull(val):
                    continue
                for validator in col.validators:
                    try:
                        if not validator(val):
                            errors.append(
                                f"Validation failed in '{col_name}' at index {i}: {val}"
                            )
                            break
                    except Exception as e:
                        errors.append(
                            f"Validator error in '{col_name}' at index {i}: {e}"
                        )

        if errors:
            raise ValueError("Schema validation failed:\n" + "\n".join(errors))
        return True
