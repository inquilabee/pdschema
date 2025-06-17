"""
Real-world data validation examples for pdschema.

This example demonstrates how to use pdschema for common real-world data
validation scenarios.
"""

import re
from datetime import datetime
from typing import Any

import pandas as pd

from pdschema.columns import Column
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Validator


# Custom validator for date format
class IsValidDate(Validator):
    def __init__(self, format: str = "%Y-%m-%d"):
        super().__init__()
        self.format = format

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, self.format)
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        return f"must be a valid date in format {self.format}"


# Custom validator for currency amount
class IsValidCurrency(Validator):
    def __init__(self, min_amount: float = 0.0, max_amount: float | None = None):
        super().__init__()
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.pattern = re.compile(r"^\$?\d+(\.\d{2})?$")

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if not self.pattern.match(value):
            return False
        # Remove $ and convert to float
        amount = float(value.replace("$", ""))
        if amount < self.min_amount:
            return False
        if self.max_amount is not None and amount > self.max_amount:
            return False
        return True

    def __str__(self) -> str:
        msg = f"must be a valid currency amount (min: ${self.min_amount:.2f}"
        if self.max_amount is not None:
            msg += f", max: ${self.max_amount:.2f}"
        return msg + ")"


# Custom validator for product SKU
class IsValidSKU(Validator):
    def __init__(self, prefix: str | None = None):
        super().__init__()
        self.prefix = prefix
        self.pattern = re.compile(r"^[A-Z0-9-]+$")

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if not self.pattern.match(value):
            return False
        if self.prefix and not value.startswith(self.prefix):
            return False
        return True

    def __str__(self) -> str:
        msg = "must be a valid SKU (uppercase letters, numbers, and hyphens only"
        if self.prefix:
            msg += f", must start with {self.prefix}"
        return msg + ")"


def ecommerce_data_validation():
    # Create a sample e-commerce DataFrame
    df = pd.DataFrame(
        {
            "order_id": ["ORD-001", "ORD-002", "ORD-003"],
            "order_date": ["2024-03-15", "2024-03-16", "invalid-date"],
            "product_sku": ["PROD-123", "invalid-sku", "PROD-456"],
            "quantity": [2, -1, 3],
            "price": ["$29.99", "$invalid", "$49.99"],
            "customer_email": ["john@example.com", "invalid-email", "jane@example.com"],
        }
    )

    # Define a schema for e-commerce data
    schema = Schema(
        [
            Column("order_id", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("order_date", str, nullable=False, validators=[IsValidDate()]),
            Column(
                "product_sku",
                str,
                nullable=False,
                validators=[IsValidSKU(prefix="PROD-")],
            ),
            Column("quantity", int, nullable=False, validators=[IsPositive()]),
            Column(
                "price",
                str,
                nullable=False,
                validators=[IsValidCurrency(min_amount=0.01)],
            ),
            Column(
                "customer_email", str, nullable=False, validators=[IsNonEmptyString()]
            ),
        ]
    )

    try:
        schema.validate(df)
    except ValueError as e:
        print("E-commerce data validation failed:")
        print(str(e))
        print("\nValidation requirements:")
        for col in schema.columns.values():
            for validator in col.validators:
                print(f"- {col.name}: {validator}")


def inventory_data_validation():
    # Create a sample inventory DataFrame
    df = pd.DataFrame(
        {
            "product_id": ["P001", "P002", "P003"],
            "name": ["Product 1", "", "Product 3"],
            "category": ["Electronics", "Invalid Category", "Books"],
            "stock_level": [100, -50, 75],
            "reorder_point": [20, 30, 40],
            "last_restock_date": ["2024-03-01", "invalid-date", "2024-03-10"],
        }
    )

    # Define a schema for inventory data
    schema = Schema(
        [
            Column("product_id", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("name", str, nullable=False, validators=[IsNonEmptyString()]),
            Column("category", str, nullable=False),
            Column("stock_level", int, nullable=False, validators=[IsPositive()]),
            Column("reorder_point", int, nullable=False, validators=[IsPositive()]),
            Column(
                "last_restock_date", str, nullable=False, validators=[IsValidDate()]
            ),
        ]
    )

    try:
        schema.validate(df)
    except ValueError as e:
        print("\nInventory data validation failed:")
        print(str(e))
        print("\nValidation requirements:")
        for col in schema.columns.values():
            for validator in col.validators:
                print(f"- {col.name}: {validator}")


if __name__ == "__main__":
    print("Running real-world validation examples...")
    ecommerce_data_validation()
    inventory_data_validation()
