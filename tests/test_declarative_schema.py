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

    # Create an invalid DataFrame (missing column)
    invalid_df = pd.DataFrame(
        {
            "id": [1, 2, 3],
        }
    )

    with pytest.raises(ValueError, match="Schema validation failed:"):
        schema.validate(invalid_df)


def test_empty_list_overrides_declared_columns():
    class Decl(Schema):
        id = Column(dtype=int, nullable=False)

    assert list(Decl().columns) == ["id"]
    assert not Decl([]).columns


def test_declarative_schema_inherits_parent_columns():
    class BaseSchema(Schema):
        id = Column(dtype=int, nullable=False)

    class ChildSchema(BaseSchema):
        name = Column(dtype=str, nullable=True)

    schema = ChildSchema()
    assert list(schema.columns) == ["id", "name"]
    df = pd.DataFrame({"id": [1], "name": ["Ada"]})
    assert schema.validate(df) is True


def test_multiple_inheritance_prefers_earlier_base():
    class SchemaA(Schema):
        id = Column(dtype=int, nullable=False)

    class SchemaB(Schema):
        id = Column(dtype=str, nullable=True)

    class SchemaC(SchemaA, SchemaB):
        pass

    assert SchemaC().columns["id"].dtype is int


def test_diamond_inheritance_follows_mro():
    class SchemaA(Schema):
        x = Column(dtype=int, nullable=False)

    class SchemaB(SchemaA):
        pass

    class SchemaC(SchemaA):
        x = Column(dtype=str, nullable=True)

    class SchemaD(SchemaB, SchemaC):
        pass

    assert SchemaD().columns["x"].dtype is int


def test_strict_schema_rejects_extra_columns():
    schema = Schema([Column("id", int, nullable=False)], strict=True)
    df = pd.DataFrame({"id": [1], "extra": ["x"]})
    with pytest.raises(ValueError, match="Unexpected columns"):
        schema.validate(df)
