"""A service for getting the scores overview for a user."""

from typing import Dict

from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.timeline import infer_timeline
from jupiter.core.domain.user.user import User
from jupiter.core.framework.base.timestamp import Timestamp


class ScoreOverviewService:
    """A service for getting the scores overview for a user."""

    async def do_it(
        self, uow: DomainUnitOfWork, user: User, right_now: Timestamp
    ) -> UserScoreOverview:
        """Get the scores overview for a user."""
        score_log = await uow.score_log_repository.load_by_parent(user.ref_id)

        score_stats_by_period: Dict[RecurringTaskPeriod, int] = {}

        for period in RecurringTaskPeriod:
            timeline = infer_timeline(period, right_now)
            score_stats = await uow.score_stats_repository.load_by_key_optional(
                (score_log.ref_id, period, timeline)
            )
            score_stats_by_period[period] = (
                score_stats.total_score if score_stats else 0
            )

        timeline_lifetime = infer_timeline(None, right_now)
        score_stats_lifetime = await uow.score_stats_repository.load_by_key_optional(
            (score_log.ref_id, None, timeline_lifetime)
        )

        return UserScoreOverview(
            daily_score=score_stats_by_period[RecurringTaskPeriod.DAILY],
            weekly_score=score_stats_by_period[RecurringTaskPeriod.WEEKLY],
            monthly_score=score_stats_by_period[RecurringTaskPeriod.MONTHLY],
            quarterly_score=score_stats_by_period[RecurringTaskPeriod.QUARTERLY],
            yearly_score=score_stats_by_period[RecurringTaskPeriod.YEARLY],
            lifetime_score=score_stats_lifetime.total_score
            if score_stats_lifetime
            else 0,
        )
