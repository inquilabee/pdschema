"""
Data cleaning and transformation examples for pdschema.

This example demonstrates how to use pdschema for data cleaning and transformation
while maintaining data quality through validation.
"""

import re
from typing import Any

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Validator


# Custom validator for cleaned string
class IsCleanString(Validator):
    def __init__(self, strip: bool = True, remove_extra_spaces: bool = True):
        super().__init__()
        self.strip = strip
        self.remove_extra_spaces = remove_extra_spaces

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        cleaned = value
        if self.strip:
            cleaned = cleaned.strip()
        if self.remove_extra_spaces:
            cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned == value

    def __str__(self) -> str:
        msg = "must be a clean string"
        if self.strip:
            msg += " (no leading/trailing whitespace"
        if self.remove_extra_spaces:
            msg += ", no extra spaces"
        return msg + ")"


# Custom validator for standardized phone number
class IsStandardizedPhone(Validator):
    def __init__(self, format: str = "(XXX) XXX-XXXX"):
        super().__init__()
        self.format = format
        self.pattern = re.compile(r"^\(\d{3}\) \d{3}-\d{4}$")

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value))

    def __str__(self) -> str:
        return f"must be a standardized phone number in format {self.format}"


def clean_and_validate_data():
    # Create a sample DataFrame with messy data
    df = pd.DataFrame(
        {
            "name": ["  John Doe  ", "Jane  Smith", "Bob  Wilson  "],
            "phone": ["123-456-7890", "(123) 456-7890", "123.456.7890"],
            "age": [" 25 ", "30", " 35 "],
            "email": ["john@example.com ", " jane@example.com", "bob@example.com  "],
        }
    )

    # Clean the data
    df["name"] = df["name"].str.strip().str.replace(r"\s+", " ", regex=True)
    df["phone"] = (
        df["phone"]
        .str.replace(r"[^\d]", "", regex=True)
        .apply(lambda x: f"({x[:3]}) {x[3:6]}-{x[6:]}")
    )
    df["age"] = pd.to_numeric(df["age"].str.strip(), errors="coerce")
    df["email"] = df["email"].str.strip()

    # Define a schema for cleaned data
    schema = Schema(
        [
            Column("name", str, nullable=False, validators=[IsCleanString()]),
            Column("phone", str, nullable=False, validators=[IsStandardizedPhone()]),
            Column("age", int, nullable=False, validators=[IsPositive()]),
            Column("email", str, nullable=False, validators=[IsNonEmptyString()]),
        ]
    )

    try:
        schema.validate(df)
        print("Data cleaning and validation successful!")
        print("\nCleaned DataFrame:")
        print(df)
    except ValueError as e:
        print("Validation failed:")
        print(str(e))


def transform_and_validate_data():
    # Create a sample DataFrame with raw data
    df = pd.DataFrame(
        {
            "raw_price": ["$1,234.56", "$2,345.67", "$3,456.78"],
            "raw_date": ["03/15/2024", "03/16/2024", "03/17/2024"],
            "raw_quantity": ["1,000", "2,000", "3,000"],
        }
    )

    # Transform the data
    df["price"] = (
        df["raw_price"].str.replace("$", "").str.replace(",", "").astype(float)
    )
    df["date"] = pd.to_datetime(df["raw_date"], format="%m/%d/%Y").dt.strftime(
        "%Y-%m-%d"
    )
    df["quantity"] = df["raw_quantity"].str.replace(",", "").astype(int)

    # Define a schema for transformed data
    schema = Schema(
        [
            Column("price", float, nullable=False, validators=[IsPositive()]),
            Column("date", str, nullable=False),
            Column("quantity", int, nullable=False, validators=[IsPositive()]),
        ]
    )

    try:
        schema.validate(df)
        print("\nData transformation and validation successful!")
        print("\nTransformed DataFrame:")
        print(df[["price", "date", "quantity"]])
    except ValueError as e:
        print("\nValidation failed:")
        print(str(e))


if __name__ == "__main__":
    print("Running data cleaning and transformation examples...")
    clean_and_validate_data()
    transform_and_validate_data()
