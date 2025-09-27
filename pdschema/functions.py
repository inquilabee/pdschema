from collections.abc import Callable
from functools import wraps
from typing import Any

import pandas as pd

from pdschema.schema import Schema


def pdfunction(
    arguments: dict[str, Schema | type] | None = None,
    outputs: dict[str, Schema | type] | None = None,
) -> Callable:
    """Decorator for validating pandas function inputs and outputs against schemas.

    Args:
        arguments: Dictionary mapping argument names to their expected schemas or types
        outputs: Dictionary mapping output names to their expected schemas

    Returns:
        Callable: Decorated function with schema validation

    Example:
        @pdfunction(
            arguments={
                "df_1": Schema([Column("id", int)]),
                "df_2": Schema([Column("value", float)]),
                "x": int,
            },
            outputs={
                "result": Schema([Column("sum", float)]),
            },
        )
        def process_data(df_1, df_2, x):
            # Function implementation
            return {"result": result_df}
    """
    arguments = arguments or {}
    outputs = outputs or {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def _validate_schema_or_type(
            name: str,
            value: Any,
            schema_or_type: Schema | type,
            is_output: bool = False,
        ):
            kind = "Output" if is_output else "Argument"
            if isinstance(schema_or_type, Schema):
                if not isinstance(value, pd.DataFrame):
                    raise TypeError(f"{kind} '{name}' must be a pandas DataFrame")
                schema_or_type.validate(value)
            elif isinstance(schema_or_type, type):
                if not isinstance(value, schema_or_type):
                    raise TypeError(f"{kind} '{name}' must be of type {schema_or_type}")
            else:
                raise TypeError(f"{kind} schema for '{name}' must be a Schema or type")

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate input arguments
            for arg_name, schema_or_type in arguments.items():
                if arg_name in kwargs:
                    _validate_schema_or_type(arg_name, kwargs[arg_name], schema_or_type, is_output=False)

            # Call the function
            result = func(*args, **kwargs)

            # Validate outputs if result is a dictionary
            if isinstance(result, dict):
                for output_name, output_schema in outputs.items():
                    if output_name not in result:
                        raise ValueError(f"Missing output: {output_name}")
                    _validate_schema_or_type(output_name, result[output_name], output_schema, is_output=True)

            return result

        return wrapper

    return decorator
