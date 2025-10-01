"""Example demonstrating the usage of the pdfunction decorator for schema validation.

This example shows how to use the pdfunction decorator to validate:
- Input DataFrame schemas
- Input types for non-DataFrame arguments
- Output DataFrame schemas
"""

import pandas as pd

from pdschema.columns import Column
from pdschema.functions import pdfunction
from pdschema.schema import Schema
from pdschema.validators import IsNonEmptyString, IsPositive, Range


@pdfunction(
    arguments={
        "users": Schema(
            [
                Column("id", int, nullable=False),
                Column("name", str, nullable=False, validators=[IsNonEmptyString]),
                Column("age", int, validators=[IsPositive(), Range(0, 120)]),
            ]
        ),
        "scores": Schema(
            [
                Column("user_id", int, nullable=False),
                Column("score", float, validators=[Range(0.0, 100.0)]),
            ]
        ),
        "min_score": float,
    },
    outputs={
        "result": Schema(
            [
                Column("user_id", int, nullable=False),
                Column("name", str, nullable=False),
                Column("age", int),
                Column("avg_score", float),
            ]
        ),
    },
)
def calculate_average_scores(users, scores, min_score):
    """Calculate average scores for users, filtering by minimum score.

    Args:
        users: DataFrame with user information
        scores: DataFrame with user scores
        min_score: Minimum score threshold

    Returns:
        DataFrame with user information and average scores
    """
    # Merge users and scores
    result = pd.merge(users, scores, left_on="id", right_on="user_id")

    # Calculate average scores
    result = result.groupby(["user_id", "name", "age"])["score"].mean().reset_index()
    result = result.rename(columns={"score": "avg_score"})

    # Filter by minimum score
    result = result[result["avg_score"] >= min_score]

    return {"result": result}


def main():
    # Create sample data
    users = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
        }
    )

    scores = pd.DataFrame(
        {
            "user_id": [1, 1, 2, 2, 3, 3],
            "score": [85.0, 90.0, 75.0, 80.0, 95.0, 100.0],
        }
    )

    # Calculate average scores with minimum threshold
    result = calculate_average_scores(
        users=users,
        scores=scores,
        min_score=85.0,
    )

    print("\nInput Users:")
    print(users)
    print("\nInput Scores:")
    print(scores)
    print("\nResult (Users with average score >= 85.0):")
    print(result["result"])


if __name__ == "__main__":
    main()
