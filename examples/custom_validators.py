"""
Custom validator examples for pdschema.

This example demonstrates how to create and use custom validators with pdschema.
"""

import re
from typing import Any

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import Validator


# Example 1: Custom validator for email format
class IsValidEmail(Validator):
    def __init__(self):
        super().__init__()
        # RFC 5322 compliant email regex
        self.email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.email_pattern.match(value))

    def __str__(self) -> str:
        return "must be a valid email address (e.g., user@domain.com)"


# Example 2: Custom validator for phone number format
class IsValidPhoneNumber(Validator):
    def __init__(self, format: str = "XXX-XXX-XXXX"):
        super().__init__()
        self.format = format
        # Convert format to regex pattern
        self.pattern = re.compile(r"^\d{3}-\d{3}-\d{4}$")

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value))

    def __str__(self) -> str:
        return f"must be a valid phone number in format {self.format}"


# Example 3: Custom validator for password strength
class IsStrongPassword(Validator):
    def __init__(self, min_length: int = 8):
        super().__init__()
        self.min_length = min_length
        self.patterns = {
            "length": lambda x: len(x) >= min_length,
            "uppercase": lambda x: any(c.isupper() for c in x),
            "lowercase": lambda x: any(c.islower() for c in x),
            "digit": lambda x: any(c.isdigit() for c in x),
            "special": lambda x: any(not c.isalnum() for c in x),
        }

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return all(check(value) for check in self.patterns.values())

    def __str__(self) -> str:
        return (
            f"must be at least {self.min_length} characters long and contain "
            "uppercase, lowercase, digit, and special character"
        )


def custom_validators_example():
    # Create a sample DataFrame
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "email": ["alice@example.com", "bob@example.com", "invalid-email"],
            "phone": ["123-456-7890", "invalid-phone", "987-654-3210"],
            "password": ["StrongP@ss1", "weakpass", "NoSpecialChar1"],
        }
    )

    # Define a schema with custom validators
    schema = Schema(
        [
            Column("name", str, nullable=False),
            Column("email", str, nullable=False, validators=[IsValidEmail()]),
            Column("phone", str, nullable=False, validators=[IsValidPhoneNumber()]),
            Column("password", str, nullable=False, validators=[IsStrongPassword()]),
        ]
    )

    try:
        schema.validate(df)
    except ValueError as e:
        print("Validation failed as expected:")
        print(str(e))
        print("\nDetailed validation requirements:")
        for col in schema.columns.values():
            for validator in col.validators:
                print(f"- {col.name}: {validator}")


if __name__ == "__main__":
    print("Running custom validators example...")
    custom_validators_example()
