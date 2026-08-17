from collections.abc import Callable
from copy import deepcopy
from typing import Self

import pandas as pd
import pyarrow as pa

from pdschema.errors import TypeCheckError
from pdschema.types import TYPE_MAPPINGS, infer_pyarrow_type_from_series
from pdschema.validators import CallableValidator, Validator

UNSUPPORTED_DTYPE = "Unsupported dtype"


class Column:
    def __init__(
        self,
        name: str | None = None,
        dtype: type | str = str,
        nullable: bool = True,
        validators: list[Validator | type[Validator] | Callable] | None = None,
    ):
        self.name = name
        self.dtype = dtype
        self.nullable = nullable
        self.validators = self._normalize_validators(validators or [])

    @staticmethod
    def _normalize_validators(
        validators: list[Validator | type[Validator] | Callable],
    ) -> list[Validator]:
        resolved: list[Validator] = []
        for validator in validators:
            if isinstance(validator, Validator):
                resolved.append(validator)
            elif isinstance(validator, type) and issubclass(validator, Validator):
                resolved.append(validator())
            elif callable(validator):
                resolved.append(CallableValidator(validator))
            else:
                raise TypeError(f"Unsupported validator: {validator!r}")
        return resolved

    def set_name(self, name: str) -> None:
        self.name = name

    def with_name(self, name: str) -> Self:
        clone = self.__class__(name, self.dtype, self.nullable)
        clone.validators = deepcopy(self.validators)
        return clone

    def to_pyarrow_type(self) -> pa.DataType:
        for mapping in TYPE_MAPPINGS:
            if self.dtype in mapping:
                return mapping[self.dtype]
        raise TypeCheckError(f"{UNSUPPORTED_DTYPE}: {self.dtype}")

    def infer_pyarrow_type(self, values: pd.Series) -> pa.DataType:
        try:
            inferred = infer_pyarrow_type_from_series(values)
            expected_type = self.to_pyarrow_type()
        except TypeError as err:
            raise TypeCheckError(f"Unsupported dtype for column {self.name!r}: series={values.dtype} ({err})") from err
        if inferred == pa.null() or str(inferred) != str(expected_type):
            raise TypeCheckError(
                f"Unsupported dtype for column {self.name!r}: series={values.dtype}, "
                f"expected {expected_type}, inferred {inferred}"
            )
        return inferred

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
                    if not validator.validate(val):
                        errors.append(f"Validation failed in '{self.name}' at index {i}: {val} ({validator})")
                except Exception as exc:
                    errors.append(f"Validator error in '{self.name}' at index {i}: {exc}")
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
        non_null = series.dropna()
        if non_null.empty:
            return None
        try:
            expected_type = self.to_pyarrow_type()
            inferred = infer_pyarrow_type_from_series(non_null)
        except TypeError as err:
            return f"Type mismatch in column '{self.name}': {err}"
        if str(inferred) != str(expected_type):
            return f"Type mismatch in column '{self.name}': expected {expected_type}, got {inferred}"
        return None
