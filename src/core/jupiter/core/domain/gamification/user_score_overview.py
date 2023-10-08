"""An overview of the scores for a user."""
from dataclasses import dataclass

from jupiter.core.framework.value import Value


@dataclass
class UserScore(Value):
    """A full view of the score for a user."""

    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int

    @staticmethod
    def new() -> "UserScore":
        """Create a new user score."""
        return UserScore(
            total_score=0,
            inbox_task_cnt=0,
            big_plan_cnt=0,
        )


@dataclass
class UserScoreOverview(Value):
    """An overview of the scores for a user."""

    daily_score: UserScore
    weekly_score: UserScore
    monthly_score: UserScore
    quarterly_score: UserScore
    yearly_score: UserScore
    lifetime_score: UserScore
    best_quarterly_daily_score: UserScore
    best_quarterly_weekly_score: UserScore
    best_quarterly_monthly_score: UserScore
    best_yearly_daily_score: UserScore
    best_yearly_weekly_score: UserScore
    best_yearly_monthly_score: UserScore
    best_yearly_quarterly_score: UserScore
    best_lifetime_daily_score: UserScore
    best_lifetime_weekly_score: UserScore
    best_lifetime_monthly_score: UserScore
    best_lifetime_quarterly_score: UserScore
    best_lifetime_yearly_score: UserScore
