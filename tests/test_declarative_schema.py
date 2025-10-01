import pandas as pd
import pytest

from pdschema.columns import Column
from pdschema.schema import Schema


def test_declarative_schema():
    class TestSchema(Schema):
        id = Column(dtype=int, nullable=False)
        name = Column(dtype=str, nullable=True)

    # Create an instance of the schema
    schema = TestSchema()

    # Assert that the schema has the declared columns
    assert "id" in schema.columns
    assert "name" in schema.columns

    # Assert column properties
    assert schema.columns["id"].dtype == int
    assert schema.columns["id"].nullable is False
    assert schema.columns["name"].dtype == str
    assert schema.columns["name"].nullable is True

    # Create a DataFrame to validate
    valid_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", None],
        }
    )

    # Validate the DataFrame
    assert schema.validate(valid_df) is True
    # assert TestSchema.validate(valid_df) is True  # Class method validation

    # Create an invalid DataFrame (missing column)
    invalid_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
        }
    )

    with pytest.raises(ValueError, match="Schema validation failed:"):
        schema.validate(invalid_df)

    # Create an invalid DataFrame (null in non-nullable column)
    invalid_df = pd.DataFrame(
        {
            "id": [1, None, 3],
            "name": ["Alice", "Bob", "Charlie"],
        }
    )

    with pytest.raises(ValueError, match="Schema validation failed:"):
        schema.validate(invalid_df)
