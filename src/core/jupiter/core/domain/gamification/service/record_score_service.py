"""A service that records scores for various actions."""
from dataclasses import dataclass
from typing import Dict, Final

from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.gamification.infra.score_log_entry_repository import (
    ScoreLogEntryAlreadyExistsError,
)
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.timeline import infer_timeline
from jupiter.core.domain.user.user import User
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.value import Value
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class RecordScoreResult(Value):
    """The result of the score recording."""

    latest_task_score: int
    score_overview: UserScoreOverview


class RecordScoreService:
    """A service that records scores for various actions."""

    _source: Final[EventSource]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        source: EventSource,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        self._source = source
        self._time_provider = time_provider

    async def record_task(
        self, uow: DomainUnitOfWork, user: User, task: InboxTask | BigPlan
    ) -> RecordScoreResult | None:
        """Record a task score."""
        if not user.is_feature_available(UserFeature.GAMIFICATION):
            return None

        if not task.status.is_completed:
            return None

        # Record the accomplishment of the task in the score log.

        score_log = await uow.score_log_repository.load_by_parent(user.ref_id)

        if isinstance(task, InboxTask):
            new_score_log_entry = ScoreLogEntry.new_from_inbox_task(
                score_log.ref_id,
                task,
                self._source,
                self._time_provider.get_current_time(),
            )
        else:
            new_score_log_entry = ScoreLogEntry.new_from_big_plan(
                score_log.ref_id,
                task,
                self._source,
                self._time_provider.get_current_time(),
            )

        try:
            await uow.score_log_entry_repository.create(new_score_log_entry)
        except ScoreLogEntryAlreadyExistsError:
            # The score log entry already exists. This entity has already been marked as done
            # or not done, and we won't do it again!
            return None

        # Update statistics at write time.

        score_stats_by_period: Dict[RecurringTaskPeriod, int] = {}

        for period in RecurringTaskPeriod:
            timeline = infer_timeline(period, self._time_provider.get_current_time())
            score_stats = await uow.score_stats_repository.load_by_key_optional(
                (score_log.ref_id, period, timeline)
            )

            if score_stats is None:
                score_stats = ScoreStats.new_score_stats(
                    score_log.ref_id,
                    period,
                    timeline,
                    self._time_provider.get_current_time(),
                ).merge_score(
                    new_score_log_entry,
                    self._source,
                    self._time_provider.get_current_time(),
                )
                await uow.score_stats_repository.create(score_stats)
            else:
                score_stats = score_stats.merge_score(
                    new_score_log_entry,
                    self._source,
                    self._time_provider.get_current_time(),
                )
                await uow.score_stats_repository.save(score_stats)

            score_stats_by_period[period] = score_stats.total_score

        timeline_lifetime = infer_timeline(None, self._time_provider.get_current_time())
        score_stats_lifetime = await uow.score_stats_repository.load_by_key_optional(
            (score_log.ref_id, None, timeline_lifetime)
        )

        if score_stats_lifetime is None:
            score_stats_lifetime = ScoreStats.new_score_stats(
                score_log.ref_id,
                None,
                timeline_lifetime,
                self._time_provider.get_current_time(),
            ).merge_score(
                new_score_log_entry,
                self._source,
                self._time_provider.get_current_time(),
            )
            await uow.score_stats_repository.create(score_stats_lifetime)
        else:
            score_stats_lifetime = score_stats_lifetime.merge_score(
                new_score_log_entry,
                self._source,
                self._time_provider.get_current_time(),
            )
            await uow.score_stats_repository.save(score_stats_lifetime)

        return RecordScoreResult(
            latest_task_score=new_score_log_entry.score,
            score_overview=UserScoreOverview(
                daily_score=score_stats_by_period[RecurringTaskPeriod.DAILY],
                weekly_score=score_stats_by_period[RecurringTaskPeriod.WEEKLY],
                monthly_score=score_stats_by_period[RecurringTaskPeriod.MONTHLY],
                quarterly_score=score_stats_by_period[RecurringTaskPeriod.QUARTERLY],
                yearly_score=score_stats_by_period[RecurringTaskPeriod.YEARLY],
                lifetime_score=score_stats_lifetime.total_score,
            ),
        )
