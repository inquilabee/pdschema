from copy import deepcopy
from typing import Callable

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
        validators: list[Validator | type[Validator] | Callable] | None = None,
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

    def validate(self, values: pd.Series) -> list[str]:
        """Validate a pandas Series against this column's constraints.

        Args:
            values: The pandas Series to validate.

        Returns:
            A list of validation error messages, if any.
        """
        errors = []
        for i, val in values.items():
            if pd.isnull(val):
                continue

            for validator in self.validators:
                try:
                    # Check if the validator is callable and apply it directly
                    if not isinstance(validator, Validator):
                        validator_instance = validator()
                    else:
                        validator_instance = validator

                    if not validator_instance.validate(val):
                        errors.append(f"Validation failed in '{self.name}' at index {i}: {val}")
                        break
                except Exception as e:
                    errors.append(f"Validator error in '{self.name}' at index {i}: {e}")
        return errors

    def check_missing(self, df: pd.DataFrame) -> str | None:
        """Check if the column is missing in the DataFrame.

        Args:
            df: The pandas DataFrame to check.

        Returns:
            An error message if the column is missing, otherwise None.
        """
        return f"Missing column: {self.name}" if self.name not in df.columns else None

    def check_nullability(self, series: pd.Series) -> str | None:
        """Check if the column violates nullability constraints.

        Args:
            series: The pandas Series to check.

        Returns:
            An error message if nullability constraints are violated, otherwise None.
        """
        if not self.nullable and series.isnull().any():
            return f"Null values found in non-nullable column: {self.name}"
        return None

    def check_type(self, series: pd.Series) -> str | None:
        """Check if the column's data type matches the expected type.

        Args:
            series: The pandas Series to check.

        Returns:
            An error message if the data type does not match, otherwise None.
        """
        try:
            pa.array(series.dropna(), type=self.to_pyarrow_type())
        except (pa.ArrowInvalid, pa.ArrowTypeError) as e:
            return f"Type mismatch in column '{self.name}': {e}"
        return None
