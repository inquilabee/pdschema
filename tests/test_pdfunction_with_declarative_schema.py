import pandas as pd
import pytest

from pdschema.columns import Column
from pdschema.functions import pdfunction
from pdschema.schema import Schema
from pdschema.validators import IsPositive


def test_pdfunction_with_declarative_schema():
    class TestSchema(Schema):
        value = Column(dtype=int, nullable=False, validators=[IsPositive()])

    @pdfunction(
        arguments={"df": TestSchema},
        outputs={"result": TestSchema},
    )
    def process_data(df):
        result = df.copy()
        result["value"] = result["value"] * 2
        return {"result": result}

    # Valid input
    df = pd.DataFrame({"value": [1, 2, 3]})
    result = process_data(df=df)
    assert isinstance(result["result"], pd.DataFrame)
    assert list(result["result"]["value"]) == [2, 4, 6]

    # Invalid input - negative values
    df_invalid = pd.DataFrame({"value": [-1, 2, 3]})
    with pytest.raises(ValueError, match="Schema validation failed"):
        process_data(df=df_invalid)
