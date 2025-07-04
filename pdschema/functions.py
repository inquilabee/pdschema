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
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate input arguments
            for arg_name, arg_value in kwargs.items():
                if arg_name in arguments:
                    schema_or_type = arguments[arg_name]
                    if isinstance(schema_or_type, Schema):
                        if not isinstance(arg_value, pd.DataFrame):
                            raise TypeError(
                                f"Argument '{arg_name}' must be a pandas DataFrame"
                            )
                        schema_or_type.validate(arg_value)
                    elif isinstance(arg_value, pd.DataFrame):
                        raise TypeError(
                            f"Argument '{arg_name}' must be of type {schema_or_type}"
                        )
                    elif not isinstance(arg_value, schema_or_type):
                        raise TypeError(
                            f"Argument '{arg_name}' must be of type {schema_or_type}"
                        )

            # Call the function
            result = func(*args, **kwargs)

            # Validate outputs if result is a dictionary
            if isinstance(result, dict):
                for output_name, output_schema in outputs.items():
                    if output_name not in result:
                        raise ValueError(f"Missing output: {output_name}")
                    if not isinstance(result[output_name], pd.DataFrame):
                        raise TypeError(
                            f"Output '{output_name}' must be a pandas DataFrame"
                        )
                    output_schema.validate(result[output_name])

            return result

        return wrapper

    return decorator
