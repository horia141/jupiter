"""A history of user scores over time."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.value import CompositeValue, Value, value


@value
class UserScoreAtDate(CompositeValue):
    """A full view of the score for a user."""

    date: ADate
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int


@value
class UserScoreHistory(CompositeValue):
    """A history of user scores over time."""

    daily_scores: list[UserScoreAtDate]
    weekly_scores: list[UserScoreAtDate]
    monthly_scores: list[UserScoreAtDate]
    quarterly_scores: list[UserScoreAtDate]
