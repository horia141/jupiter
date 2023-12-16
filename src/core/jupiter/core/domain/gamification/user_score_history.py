"""A history of user scores over time."""
from dataclasses import dataclass

from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.value import Value


@dataclass
class UserScoreAtDate(Value):
    """A full view of the score for a user."""

    date: ADate
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int


@dataclass
class UserScoreHistory(Value):
    """A history of user scores over time."""

    daily_scores: list[UserScoreAtDate]
    weekly_scores: list[UserScoreAtDate]
    monthly_scores: list[UserScoreAtDate]
    quarterly_scores: list[UserScoreAtDate]
