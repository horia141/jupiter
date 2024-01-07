"""An overview of the scores for a user."""

from jupiter.core.framework.value import Value, value


@value
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


@value
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

    @staticmethod
    def empty() -> "UserScoreOverview":
        """Create an empty user score overview."""
        return UserScoreOverview(
            daily_score=UserScore.new(),
            weekly_score=UserScore.new(),
            monthly_score=UserScore.new(),
            quarterly_score=UserScore.new(),
            yearly_score=UserScore.new(),
            lifetime_score=UserScore.new(),
            best_quarterly_daily_score=UserScore.new(),
            best_quarterly_weekly_score=UserScore.new(),
            best_quarterly_monthly_score=UserScore.new(),
            best_yearly_daily_score=UserScore.new(),
            best_yearly_weekly_score=UserScore.new(),
            best_yearly_monthly_score=UserScore.new(),
            best_yearly_quarterly_score=UserScore.new(),
            best_lifetime_daily_score=UserScore.new(),
            best_lifetime_weekly_score=UserScore.new(),
            best_lifetime_monthly_score=UserScore.new(),
            best_lifetime_quarterly_score=UserScore.new(),
            best_lifetime_yearly_score=UserScore.new(),
        )
