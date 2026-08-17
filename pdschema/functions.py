from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import ParamSpec, TypeVar, cast

import pandas as pd

from pdschema.errors import FunctionSchemaError, SchemaValidationError
from pdschema.schema import Schema

P = ParamSpec("P")
R = TypeVar("R")


def pdfunction(
    arguments: dict[str, Schema | type] | None = None,
    outputs: dict[str, Schema | type] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for validating pandas function inputs and outputs against schemas.

    Every name in ``arguments`` is validated whether the caller used positional
    or keyword arguments. ``outputs`` expects the wrapped function to return a
    dict of DataFrames (or other declared types).
    """
    arguments = arguments or {}
    outputs = outputs or {}

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        func_signature = signature(func)

        def _validate_schema_or_type(
            name: str,
            value: object,
            schema_or_type: Schema | type,
            *,
            is_output: bool = False,
        ) -> None:
            kind = "Output" if is_output else "Argument"
            if isinstance(schema_or_type, Schema) or (
                isinstance(schema_or_type, type) and issubclass(schema_or_type, Schema)
            ):
                if not isinstance(value, pd.DataFrame):
                    raise FunctionSchemaError(f"{kind} '{name}' must be a pandas DataFrame")
                schema_instance = schema_or_type() if isinstance(schema_or_type, type) else schema_or_type
                schema_instance.validate(value)
            elif isinstance(schema_or_type, type):
                if not isinstance(value, schema_or_type):
                    raise FunctionSchemaError(f"{kind} '{name}' must be of type {schema_or_type}")
            else:
                raise FunctionSchemaError(f"{kind} schema for '{name}' must be a Schema or type")

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            bound = func_signature.bind(*args, **kwargs)
            bound.apply_defaults()
            for arg_name, schema_or_type in arguments.items():
                if arg_name not in bound.arguments:
                    raise FunctionSchemaError(f"Missing required argument: {arg_name}")
                _validate_schema_or_type(arg_name, bound.arguments[arg_name], schema_or_type, is_output=False)

            result = func(*args, **kwargs)

            if isinstance(result, dict):
                payload = cast(dict[str, object], result)
                for output_name, output_schema in outputs.items():
                    if output_name not in payload:
                        raise SchemaValidationError(f"Missing output: {output_name}")
                    _validate_schema_or_type(output_name, payload[output_name], output_schema, is_output=True)

            return result

        return wrapper

    return decorator
