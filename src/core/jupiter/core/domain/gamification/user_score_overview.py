"""An overview of the scores for a user."""

from dataclasses import dataclass

from jupiter.core.framework.value import Value


@dataclass
class UserScoreOverview(Value):
    """An overview of the scores for a user."""

    daily_score: int
    weekly_score: int
    monthly_score: int
    quarterly_score: int
    yearly_score: int
    lifetime_score: int
