import pandas as pd
import pytest

from pdschema.columns import Column
from pdschema.functions import pdfunction
from pdschema.schema import Schema
from pdschema.validators import IsPositive, Range

VAL = 50


def test_pdfunction_basic():
    @pdfunction(
        arguments={
            "df": Schema([Column("value", int, validators=[IsPositive()])]),
            "multiplier": int,
        },
        outputs={
            "result": Schema([Column("value", int, validators=[IsPositive()])]),
        },
    )
    def multiply_values(df, multiplier):
        result = df.copy()
        result["value"] = result["value"] * multiplier
        return {"result": result}

    # Valid input
    df = pd.DataFrame({"value": [1, 2, 3]})
    result = multiply_values(df=df, multiplier=2)
    assert isinstance(result["result"], pd.DataFrame)
    assert list(result["result"]["value"]) == [2, 4, 6]

    # Invalid input - negative values
    df_invalid = pd.DataFrame({"value": [-1, 2, 3]})
    with pytest.raises(ValueError, match="Schema validation failed"):
        multiply_values(df=df_invalid, multiplier=2)

    # Invalid input - wrong type
    with pytest.raises(
        TypeError, match="Argument 'multiplier' must be of type <class 'int'>"
    ):
        multiply_values(df=df, multiplier="2")


def test_pdfunction_multiple_outputs():
    @pdfunction(
        arguments={
            "df": Schema([Column("value", float, validators=[Range(0.0, 100.0)])]),
        },
        outputs={
            "above_50": Schema([Column("value", float)]),
            "below_50": Schema([Column("value", float)]),
        },
    )
    def split_by_threshold(df):
        above = df[df["value"] > VAL].copy()
        below = df[df["value"] <= VAL].copy()
        return {"above_50": above, "below_50": below}

    # Valid input
    df = pd.DataFrame({"value": [25.0, 75.0, 50.0]})
    result = split_by_threshold(df=df)
    assert isinstance(result["above_50"], pd.DataFrame)
    assert isinstance(result["below_50"], pd.DataFrame)
    assert list(result["above_50"]["value"]) == [75.0]
    assert list(result["below_50"]["value"]) == [25.0, 50.0]

    # Invalid input - out of range
    df_invalid = pd.DataFrame({"value": [25.0, 150.0, 50.0]})
    with pytest.raises(ValueError, match="Validation failed in 'value'"):
        split_by_threshold(df=df_invalid)


def test_pdfunction_missing_output():
    @pdfunction(
        arguments={
            "df": Schema([Column("value", int)]),
        },
        outputs={
            "result": Schema([Column("value", int)]),
        },
    )
    def process_data(df):
        return {}  # Missing output

    df = pd.DataFrame({"value": [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing output: result"):
        process_data(df=df)


def test_pdfunction_wrong_output_type():
    @pdfunction(
        arguments={
            "df": Schema([Column("value", int)]),
        },
        outputs={
            "result": Schema([Column("value", int)]),
        },
    )
    def process_data(df):
        return {"result": "not a dataframe"}

    df = pd.DataFrame({"value": [1, 2, 3]})
    with pytest.raises(TypeError, match="Output 'result' must be a pandas DataFrame"):
        process_data(df=df)


def test_pdfunction_no_validation():
    @pdfunction()
    def no_validation(df):
        return {"result": df}

    df = pd.DataFrame({"value": [1, 2, 3]})
    result = no_validation(df=df)
    assert isinstance(result["result"], pd.DataFrame)
    assert list(result["result"]["value"]) == [1, 2, 3]
