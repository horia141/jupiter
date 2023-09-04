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
    best_quarterly_daily_score: int
    best_quarterly_weekly_score: int
    best_quarterly_monthly_score: int
    best_yearly_daily_score: int
    best_yearly_weekly_score: int
    best_yearly_monthly_score: int
    best_yearly_quarterly_score: int
    best_lifetime_daily_score: int
    best_lifetime_weekly_score: int
    best_lifetime_monthly_score: int
    best_lifetime_quarterly_score: int
    best_lifetime_yearly_score: int
