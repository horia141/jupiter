"""A service that records scores for various actions."""
import asyncio

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.domain.gamification.infra.score_log_entry_repository import (
    ScoreLogEntryAlreadyExistsError,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gamification.score_period_best import ScorePeriodBest
from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.user.user import User
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.value import Value, value


@value
class RecordScoreResult(Value):
    """The result of the score recording."""

    latest_task_score: int
    has_lucky_puppy_bonus: bool | None
    score_overview: UserScoreOverview


class RecordScoreService:
    """A service that records scores for various actions."""

    async def record_task(
        self,
        ctx: DomainContext,
        uow: DomainUnitOfWork,
        user: User,
        task: InboxTask | BigPlan,
    ) -> RecordScoreResult | None:
        """Record a task score."""
        if not task.status.is_completed:
            return None

        # Record the accomplishment of the task in the score log.

        score_log = await uow.score_log_repository.load_by_parent(user.ref_id)

        if isinstance(task, InboxTask):
            new_score_log_entry = ScoreLogEntry.new_from_inbox_task(
                ctx,
                score_log.ref_id,
                task,
            )
        else:
            new_score_log_entry = ScoreLogEntry.new_from_big_plan(
                ctx,
                score_log.ref_id,
                task,
            )

        try:
            await uow.score_log_entry_repository.create(new_score_log_entry)
        except ScoreLogEntryAlreadyExistsError:
            # The score log entry already exists. This entity has already been marked as done
            # or not done, and we won't do it again!
            return None

        # Update statistics at write time.

        (
            daily_score_stats,
            weekly_score_stats,
            monthly_score_stats,
            quarterly_score_stats,
            yearly_score_stats,
            lifetime_score_stats,
        ) = await asyncio.gather(
            self._update_current_stats(
                ctx, RecurringTaskPeriod.DAILY, uow, score_log, new_score_log_entry
            ),
            self._update_current_stats(
                ctx, RecurringTaskPeriod.WEEKLY, uow, score_log, new_score_log_entry
            ),
            self._update_current_stats(
                ctx, RecurringTaskPeriod.MONTHLY, uow, score_log, new_score_log_entry
            ),
            self._update_current_stats(
                ctx, RecurringTaskPeriod.QUARTERLY, uow, score_log, new_score_log_entry
            ),
            self._update_current_stats(
                ctx, RecurringTaskPeriod.YEARLY, uow, score_log, new_score_log_entry
            ),
            self._update_current_stats(ctx, None, uow, score_log, new_score_log_entry),
        )

        # Update high scores at write time.

        (
            best_quarterly_daily,
            best_quarterly_weekly,
            best_quarterly_monthly,
        ) = await asyncio.gather(
            self._update_best(
                ctx,
                RecurringTaskPeriod.QUARTERLY,
                RecurringTaskPeriod.DAILY,
                daily_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                RecurringTaskPeriod.QUARTERLY,
                RecurringTaskPeriod.WEEKLY,
                weekly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                RecurringTaskPeriod.QUARTERLY,
                RecurringTaskPeriod.MONTHLY,
                monthly_score_stats,
                uow,
                score_log,
            ),
        )

        (
            best_yearly_daily,
            best_yearly_weekly,
            best_yearly_monthly,
            best_yearly_quarterly,
        ) = await asyncio.gather(
            self._update_best(
                ctx,
                RecurringTaskPeriod.YEARLY,
                RecurringTaskPeriod.DAILY,
                daily_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                RecurringTaskPeriod.YEARLY,
                RecurringTaskPeriod.WEEKLY,
                weekly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                RecurringTaskPeriod.YEARLY,
                RecurringTaskPeriod.MONTHLY,
                monthly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                RecurringTaskPeriod.YEARLY,
                RecurringTaskPeriod.QUARTERLY,
                quarterly_score_stats,
                uow,
                score_log,
            ),
        )

        (
            best_lifetime_daily,
            best_lifetime_weekly,
            best_lifetime_monthly,
            best_lifetime_quarterly,
            best_lifetime_yearly,
        ) = await asyncio.gather(
            self._update_best(
                ctx,
                None,
                RecurringTaskPeriod.DAILY,
                daily_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                None,
                RecurringTaskPeriod.WEEKLY,
                weekly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                None,
                RecurringTaskPeriod.MONTHLY,
                monthly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                None,
                RecurringTaskPeriod.QUARTERLY,
                quarterly_score_stats,
                uow,
                score_log,
            ),
            self._update_best(
                ctx,
                None,
                RecurringTaskPeriod.YEARLY,
                yearly_score_stats,
                uow,
                score_log,
            ),
        )

        return RecordScoreResult(
            latest_task_score=new_score_log_entry.score,
            has_lucky_puppy_bonus=new_score_log_entry.has_lucky_puppy_bonus,
            score_overview=UserScoreOverview(
                daily_score=daily_score_stats.to_user_score(),
                weekly_score=weekly_score_stats.to_user_score(),
                monthly_score=monthly_score_stats.to_user_score(),
                quarterly_score=quarterly_score_stats.to_user_score(),
                yearly_score=yearly_score_stats.to_user_score(),
                lifetime_score=lifetime_score_stats.to_user_score(),
                best_quarterly_daily_score=best_quarterly_daily.to_user_score(),
                best_quarterly_weekly_score=best_quarterly_weekly.to_user_score(),
                best_quarterly_monthly_score=best_quarterly_monthly.to_user_score(),
                best_yearly_daily_score=best_yearly_daily.to_user_score(),
                best_yearly_weekly_score=best_yearly_weekly.to_user_score(),
                best_yearly_monthly_score=best_yearly_monthly.to_user_score(),
                best_yearly_quarterly_score=best_yearly_quarterly.to_user_score(),
                best_lifetime_daily_score=best_lifetime_daily.to_user_score(),
                best_lifetime_weekly_score=best_lifetime_weekly.to_user_score(),
                best_lifetime_monthly_score=best_lifetime_monthly.to_user_score(),
                best_lifetime_quarterly_score=best_lifetime_quarterly.to_user_score(),
                best_lifetime_yearly_score=best_lifetime_yearly.to_user_score(),
            ),
        )

    async def _update_current_stats(
        self,
        ctx: DomainContext,
        period: RecurringTaskPeriod | None,
        uow: DomainUnitOfWork,
        score_log: ScoreLog,
        score_log_entry: ScoreLogEntry,
    ) -> ScoreStats:
        timeline = infer_timeline(period, ctx.action_timestamp)
        score_stats = await uow.score_stats_repository.load_by_key_optional(
            (score_log.ref_id, period, timeline)
        )

        if score_stats is None:
            score_stats = ScoreStats.new_score_stats(
                ctx,
                score_log.ref_id,
                period,
                timeline,
            ).merge_score(
                ctx,
                score_log_entry,
            )
            score_stats = await uow.score_stats_repository.create(score_stats)
        else:
            score_stats = score_stats.merge_score(
                ctx,
                score_log_entry,
            )
            score_stats = await uow.score_stats_repository.save(score_stats)

        return score_stats

    async def _update_best(
        self,
        ctx: DomainContext,
        period: RecurringTaskPeriod | None,
        sub_period: RecurringTaskPeriod,
        score_stats: ScoreStats,
        uow: DomainUnitOfWork,
        score_log: ScoreLog,
    ) -> ScorePeriodBest:
        timeline = infer_timeline(period, ctx.action_timestamp)
        score_period_best = await uow.score_period_best_repository.load_by_key_optional(
            (score_log.ref_id, period, timeline, sub_period)
        )

        if score_period_best is None:
            score_period_best = ScorePeriodBest.new_score_period_best(
                ctx,
                score_log.ref_id,
                period,
                timeline,
                sub_period,
            ).update_to_max(ctx, score_stats)
            score_period_best = await uow.score_period_best_repository.create(
                score_period_best
            )
        else:
            score_period_best = score_period_best.update_to_max(
                ctx,
                score_stats,
            )
            score_period_best = await uow.score_period_best_repository.save(
                score_period_best
            )

        return score_period_best
