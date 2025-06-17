"""
Complex schema examples for pdschema.

This example demonstrates how to create and use complex schemas with multiple validators
and nested data structures.
"""

import json
from typing import Any

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Validator


# Custom validator for JSON string validation
class IsValidJSON(Validator):
    def __init__(self):
        super().__init__()

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False


# Custom validator for address JSON validation
class IsValidAddress(Validator):
    def __init__(self):
        super().__init__()

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        try:
            data = json.loads(value)
            if not isinstance(data, dict):
                return False
            required_fields = {"street", "city", "zip"}
            return all(field in data for field in required_fields)
        except json.JSONDecodeError:
            return False


def complex_schema_example():
    # Create a sample DataFrame with nested data as JSON strings
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "address": [
                json.dumps({"street": "123 Main St", "city": "Boston", "zip": "02108"}),
                json.dumps(
                    {"street": "456 Oak Ave", "city": "New York", "zip": "10001"}
                ),
                json.dumps(
                    {"street": "789 Pine Rd", "city": "Chicago", "zip": "60601"}
                ),
            ],
            "scores": [
                json.dumps({"math": 95, "science": 88, "english": 92}),
                json.dumps({"math": 88, "science": 92, "english": 85}),
                json.dumps({"math": 92, "science": 85, "english": 90}),
            ],
        }
    )

    # Define a complex schema
    schema = Schema(
        [
            Column("id", int, nullable=False, validators=[IsPositive()]),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("age", int, nullable=False, validators=[IsPositive()]),
            Column("address", str, nullable=False, validators=[IsValidAddress()]),
            Column("scores", str, nullable=False, validators=[IsValidJSON()]),
        ]
    )

    # Validate the DataFrame
    schema.validate(df)
    print("Complex schema validation passed!")


def nested_validation_example():
    # Create a sample DataFrame with list data as JSON strings
    df = pd.DataFrame(
        {
            "id": [1, 2],
            "tags": [
                json.dumps(["python", "data"]),
                json.dumps(["schema", "validation"]),
            ],
            "metadata": [
                json.dumps({"version": "1.0", "author": "Alice"}),
                json.dumps({"version": "2.0", "author": "Bob"}),
            ],
        }
    )

    # Define a schema for nested data
    schema = Schema(
        [
            Column("id", int, nullable=False),
            Column("tags", str, nullable=False, validators=[IsValidJSON()]),
            Column("metadata", str, nullable=False, validators=[IsValidJSON()]),
        ]
    )

    # Validate the DataFrame
    schema.validate(df)
    print("Nested validation passed!")


if __name__ == "__main__":
    print("Running complex schema examples...")
    complex_schema_example()
    nested_validation_example()
