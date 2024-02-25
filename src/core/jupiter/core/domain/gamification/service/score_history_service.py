"""The service for getting the scores history for a user."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.gamification.infra.score_stats_repository import (
    ScoreStatsRepository,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.user_score_history import UserScoreHistory
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.user.user import User
from jupiter.core.framework.base.timestamp import Timestamp


class ScoreHistoryService:
    """A service for getting the scores history for a user."""

    async def do_it(
        self, uow: DomainUnitOfWork, user: User, right_now: Timestamp
    ) -> UserScoreHistory:
        """Retrieve the history of scores for a user."""
        score_log = await uow.get_for(ScoreLog).load_by_parent(user.ref_id)

        today = ADate.from_date(right_now.as_date())
        daily_lower_limit = today.subtract_days(90)
        weekly_lower_limit = today.subtract_days(365)
        monthly_lower_limit = today.subtract_days(365 * 2)
        quarterly_lower_limit = today.subtract_days(365 * 5)

        daily_score_stats = await uow.get(ScoreStatsRepository).find_all_in_timerange(
            score_log.ref_id, RecurringTaskPeriod.DAILY, daily_lower_limit, today
        )
        weekly_score_stats = await uow.get(ScoreStatsRepository).find_all_in_timerange(
            score_log.ref_id, RecurringTaskPeriod.WEEKLY, weekly_lower_limit, today
        )
        monthly_score_stats = await uow.get(ScoreStatsRepository).find_all_in_timerange(
            score_log.ref_id, RecurringTaskPeriod.MONTHLY, monthly_lower_limit, today
        )
        quarterly_score_stats = await uow.get(
            ScoreStatsRepository
        ).find_all_in_timerange(
            score_log.ref_id,
            RecurringTaskPeriod.QUARTERLY,
            quarterly_lower_limit,
            today,
        )

        return UserScoreHistory(
            daily_scores=[f.to_user_score_at_date() for f in daily_score_stats],
            weekly_scores=[f.to_user_score_at_date() for f in weekly_score_stats],
            monthly_scores=[f.to_user_score_at_date() for f in monthly_score_stats],
            quarterly_scores=[f.to_user_score_at_date() for f in quarterly_score_stats],
        )
