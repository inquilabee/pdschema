from collections.abc import Callable
from copy import deepcopy
from typing import Self

import pandas as pd
import pyarrow as pa

from pdschema.errors import PdSchemaError, TypeCheckError
from pdschema.types import TYPE_MAPPINGS, TypeRegistry, infer_pyarrow_type_from_series
from pdschema.validators import CallableValidator, Validator

UNSUPPORTED_DTYPE = "Unsupported dtype"
AT_INDEX = " at index "


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
        dtype = self.dtype
        pyarrow_dtype = getattr(dtype, "pyarrow_dtype", None)
        if pyarrow_dtype is not None:
            return pyarrow_dtype
        if isinstance(dtype, str) and dtype in TypeRegistry.PANDAS_TO_PA:
            return TypeRegistry.PANDAS_TO_PA[dtype]
        name = str(dtype)
        if name in TypeRegistry.PANDAS_TO_PA:
            return TypeRegistry.PANDAS_TO_PA[name]
        for mapping in TYPE_MAPPINGS:
            if dtype in mapping:
                return mapping[dtype]
        raise TypeCheckError(f"{UNSUPPORTED_DTYPE}: {dtype}")

    def infer_pyarrow_type(self, values: pd.Series) -> pa.DataType:
        try:
            inferred = infer_pyarrow_type_from_series(values)
            expected_type = self.to_pyarrow_type()
        except TypeError as err:
            raise TypeCheckError(f"Unsupported dtype for column {self.name!r}: series={values.dtype} ({err})") from err
        if inferred == pa.null() or (
            str(inferred) != str(expected_type)
            and not TypeRegistry.types_compatible(expected_type, inferred, self.dtype)
        ):
            raise TypeCheckError(
                f"Unsupported dtype for column {self.name!r}: series={values.dtype}, "
                f"expected {expected_type}, inferred {inferred}"
            )
        return inferred

    def _fmt_error(self, i: object, val: object, v: Validator) -> str:
        return f"Validation failed in '{self.name}'{AT_INDEX}{i}: {val} ({v})"

    def validate(self, values: pd.Series) -> list[str]:
        """Validate a pandas Series against this column's constraints.

        Uses vectorized operations for built-in validators when possible,
        falling back to scalar iteration for custom validators.
        """
        non_null = values.dropna()
        if non_null.empty:
            return []

        vec_vals, scalar_vals = self._split_validators(non_null)
        errors: list[str] = []

        if vec_vals:
            scalar_check_indices = self._validate_vectorized(non_null, vec_vals, errors)
        else:
            scalar_check_indices = non_null.index

        if scalar_vals and self.name is not None:
            self._validate_scalar(self.name, non_null, scalar_check_indices, scalar_vals, errors)

        return errors

    def _split_validators(self, series: pd.Series) -> tuple[list[Validator], list[Validator]]:
        vec: list[Validator] = []
        scalar: list[Validator] = []
        for v in self.validators:
            if v.validate_vector(series) is not None:
                vec.append(v)
            else:
                scalar.append(v)
        return vec, scalar

    def _validate_vectorized(
        self,
        non_null: pd.Series,
        vec_vals: list[Validator],
        errors: list[str],
    ) -> pd.Index:
        combined = pd.Series(True, index=non_null.index)
        vec_masks: list[tuple[Validator, pd.Series]] = []
        for v in vec_vals:
            mask = v.validate_vector(non_null)
            if mask is not None:
                vec_masks.append((v, mask))
                combined &= mask
        vec_failing = combined[~combined].index
        for i in vec_failing:
            val = non_null.at[i]
            for v, mask in vec_masks:
                if not mask.at[i]:
                    errors.append(self._fmt_error(i, val, v))
        return combined[combined].index

    @staticmethod
    def _validate_scalar(
        col_name: str,
        non_null: pd.Series,
        indices: pd.Index,
        scalar_vals: list[Validator],
        errors: list[str],
    ) -> None:
        for i in indices:
            val = non_null.at[i]
            for v in scalar_vals:
                try:
                    if not v.validate(val):
                        errors.append(f"Validation failed in '{col_name}'{AT_INDEX}{i}: {val} ({v})")
                except (TypeError, ValueError, PdSchemaError) as exc:
                    errors.append(f"Validator error in '{col_name}'{AT_INDEX}{i}: {exc}")

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
        if str(inferred) != str(expected_type) and not TypeRegistry.types_compatible(
            expected_type, inferred, self.dtype
        ):
            return f"Type mismatch in column '{self.name}': expected {expected_type}, got {inferred}"
        return None
