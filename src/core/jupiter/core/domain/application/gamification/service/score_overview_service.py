"""A service for getting the scores overview for a user."""
import asyncio

from jupiter.core.domain.application.gamification.score_log import ScoreLog
from jupiter.core.domain.application.gamification.score_period_best import (
    ScorePeriodBestRepository,
)
from jupiter.core.domain.application.gamification.score_stats import (
    ScoreStatsRepository,
)
from jupiter.core.domain.application.gamification.user_score_overview import (
    UserScore,
    UserScoreOverview,
)
from jupiter.core.domain.concept.user.user import User
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.timestamp import Timestamp


class ScoreOverviewService:
    """A service for getting the scores overview for a user."""

    async def do_it(
        self, uow: DomainUnitOfWork, user: User, right_now: Timestamp
    ) -> UserScoreOverview:
        """Get the scores overview for a user."""
        score_log = await uow.get_for(ScoreLog).load_by_parent(user.ref_id)

        (
            daily_score,
            weekly_score,
            monthly_score,
            quarterly_score,
            yearly_score,
            lifetime_score,
        ) = await asyncio.gather(
            self._load_stats(uow, score_log, RecurringTaskPeriod.DAILY, right_now),
            self._load_stats(uow, score_log, RecurringTaskPeriod.WEEKLY, right_now),
            self._load_stats(uow, score_log, RecurringTaskPeriod.MONTHLY, right_now),
            self._load_stats(uow, score_log, RecurringTaskPeriod.QUARTERLY, right_now),
            self._load_stats(uow, score_log, RecurringTaskPeriod.YEARLY, right_now),
            self._load_stats(uow, score_log, None, right_now),
        )

        (
            best_quarterly_daily_score,
            best_quarterly_weekly_score,
            best_quarterly_monthly_score,
        ) = await asyncio.gather(
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.QUARTERLY,
                right_now,
                RecurringTaskPeriod.DAILY,
            ),
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.QUARTERLY,
                right_now,
                RecurringTaskPeriod.WEEKLY,
            ),
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.QUARTERLY,
                right_now,
                RecurringTaskPeriod.MONTHLY,
            ),
        )

        (
            best_yearly_daily_score,
            best_yearly_weekly_score,
            best_yearly_monthly_score,
            best_yearly_quarterly_score,
        ) = await asyncio.gather(
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.YEARLY,
                right_now,
                RecurringTaskPeriod.DAILY,
            ),
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.YEARLY,
                right_now,
                RecurringTaskPeriod.WEEKLY,
            ),
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.YEARLY,
                right_now,
                RecurringTaskPeriod.MONTHLY,
            ),
            self._load_period_best(
                uow,
                score_log,
                RecurringTaskPeriod.YEARLY,
                right_now,
                RecurringTaskPeriod.QUARTERLY,
            ),
        )

        (
            best_lifetime_daily_score,
            best_lifetime_weekly_score,
            best_lifetime_monthly_score,
            best_lifetime_quarterly_score,
            best_lifetime_yearly_score,
        ) = await asyncio.gather(
            self._load_period_best(
                uow, score_log, None, right_now, RecurringTaskPeriod.DAILY
            ),
            self._load_period_best(
                uow, score_log, None, right_now, RecurringTaskPeriod.WEEKLY
            ),
            self._load_period_best(
                uow, score_log, None, right_now, RecurringTaskPeriod.MONTHLY
            ),
            self._load_period_best(
                uow, score_log, None, right_now, RecurringTaskPeriod.QUARTERLY
            ),
            self._load_period_best(
                uow, score_log, None, right_now, RecurringTaskPeriod.YEARLY
            ),
        )

        return UserScoreOverview(
            daily_score=daily_score,
            weekly_score=weekly_score,
            monthly_score=monthly_score,
            quarterly_score=quarterly_score,
            yearly_score=yearly_score,
            lifetime_score=lifetime_score,
            best_quarterly_daily_score=best_quarterly_daily_score,
            best_quarterly_weekly_score=best_quarterly_weekly_score,
            best_quarterly_monthly_score=best_quarterly_monthly_score,
            best_yearly_daily_score=best_yearly_daily_score,
            best_yearly_weekly_score=best_yearly_weekly_score,
            best_yearly_monthly_score=best_yearly_monthly_score,
            best_yearly_quarterly_score=best_yearly_quarterly_score,
            best_lifetime_daily_score=best_lifetime_daily_score,
            best_lifetime_weekly_score=best_lifetime_weekly_score,
            best_lifetime_monthly_score=best_lifetime_monthly_score,
            best_lifetime_quarterly_score=best_lifetime_quarterly_score,
            best_lifetime_yearly_score=best_lifetime_yearly_score,
        )

    async def _load_stats(
        self,
        uow: DomainUnitOfWork,
        score_log: ScoreLog,
        period: RecurringTaskPeriod | None,
        right_now: Timestamp,
    ) -> UserScore:
        timeline = infer_timeline(period, right_now)
        score_stats = await uow.get(ScoreStatsRepository).load_by_key_optional(
            (score_log.ref_id, period, timeline)
        )
        return score_stats.to_user_score() if score_stats else UserScore.new()

    async def _load_period_best(
        self,
        uow: DomainUnitOfWork,
        score_log: ScoreLog,
        period: RecurringTaskPeriod | None,
        right_now: Timestamp,
        sub_period: RecurringTaskPeriod,
    ) -> UserScore:
        timeline = infer_timeline(period, right_now)
        score_period_best = await uow.get(
            ScorePeriodBestRepository
        ).load_by_key_optional((score_log.ref_id, period, timeline, sub_period))
        return (
            score_period_best.to_user_score() if score_period_best else UserScore.new()
        )
