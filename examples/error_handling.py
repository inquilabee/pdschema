"""
Error handling examples for pdschema.

This example demonstrates how to handle validation errors and exceptions
when working with pdschema.
"""

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Range


def error_handling_example():
    # Create a sample DataFrame with invalid data
    df = pd.DataFrame(
        {
            "name": ["Alice", "", "Charlie"],  # Empty string
            "age": [25, -5, 35],  # Negative age
            "score": [95.5, 88.0, 150.0],  # Score out of range
        }
    )

    # Define a schema
    schema = Schema(
        [
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("age", int, nullable=False, validators=[IsPositive()]),
            Column("score", float, validators=[Range(0, 100)]),
        ]
    )

    try:
        schema.validate(df)
    except ValueError as e:
        print("Validation failed with the following errors:")
        print(str(e))


def multiple_errors_example():
    # Create a DataFrame with multiple validation issues
    df = pd.DataFrame(
        {
            "id": [1, None, 3],  # Missing value
            "email": ["invalid", "test@", "valid@example.com"],  # Invalid emails
            "age": ["not a number", 25, -10],  # Invalid age values
        }
    )

    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("email", str, nullable=False),
            Column("age", int, nullable=False, validators=[IsPositive()]),
        ]
    )

    try:
        schema.validate(df)
    except ValueError as e:
        print("\nMultiple validation errors:")
        print(str(e))


def custom_error_handling():
    # Create a DataFrame with custom validation needs
    df = pd.DataFrame(
        {
            "status": ["active", "inactive", "unknown"],
            "priority": ["high", "medium", "invalid"],
        }
    )

    schema = Schema([Column("status", str, nullable=False), Column("priority", str, nullable=False)])

    try:
        schema.validate(df)
    except ValueError as e:
        print("\nCustom validation errors:")
        print(str(e))
    except Exception as e:
        print(f"\nUnexpected error: {e!s}")


if __name__ == "__main__":
    print("Running error handling examples...")
    error_handling_example()
    multiple_errors_example()
    custom_error_handling()
