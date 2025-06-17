"""
Basic usage examples of pdschema.

This example demonstrates common patterns for schema validation using pdschema.
"""

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Range


# Example 1: Basic schema with simple validators
def basic_schema_example():
    # Create a sample DataFrame
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "score": [95.5, 88.0, 91.2],
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

    # Validate the DataFrame
    schema.validate(df)
    print("Basic schema validation passed!")


# Example 2: Schema with nullable columns
def nullable_columns_example():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", None, "Charlie"],
            "email": ["alice@example.com", "bob@example.com", None],
        }
    )

    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("name", str, nullable=True),
            Column("email", str, nullable=True),
        ]
    )

    schema.validate(df)
    print("Nullable columns validation passed!")


if __name__ == "__main__":
    print("Running basic usage examples...")
    basic_schema_example()
    nullable_columns_example()
