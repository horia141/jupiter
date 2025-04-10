"""Statistics about scores for a particular time interval."""

import abc

from jupiter.core.domain.application.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.application.gamification.score_source import ScoreSource
from jupiter.core.domain.application.gamification.user_score_history import (
    UserScoreAtDate,
)
from jupiter.core.domain.application.gamification.user_score_overview import UserScore
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.record import Record, create_record_action, record
from jupiter.core.framework.repository import RecordRepository


@record
class ScoreStats(Record):
    """Statistics about scores for a particular time interval."""

    score_log: ParentLink
    period: RecurringTaskPeriod | None
    timeline: str
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int

    @staticmethod
    @create_record_action
    def new_score_stats(
        ctx: DomainContext,
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod | None,
        timeline: str,
    ) -> "ScoreStats":
        """Create a score stats for a given period and timeline."""
        return ScoreStats._create(
            ctx,
            score_log=ParentLink(score_log_ref_id),
            period=period,
            timeline=timeline,
            total_score=0,
            inbox_task_cnt=0,
            big_plan_cnt=0,
        )

    def merge_score(
        self,
        ctx: DomainContext,
        score_log_entry: ScoreLogEntry,
    ) -> "ScoreStats":
        """Merge a score log entry into the score stats."""
        return self._new_version(
            ctx,
            total_score=max(0, self.total_score + score_log_entry.score),
            inbox_task_cnt=self.inbox_task_cnt
            + (1 if score_log_entry.source == ScoreSource.INBOX_TASK else 0),
            big_plan_cnt=self.big_plan_cnt
            + (1 if score_log_entry.source == ScoreSource.BIG_PLAN else 0),
        )

    @property
    def raw_key(self) -> object:
        """The raw key of the score stats."""
        return self.key

    @property
    def key(self) -> tuple[EntityId, RecurringTaskPeriod | None, str]:
        """The key of the score stats."""
        return self.score_log.ref_id, self.period, self.timeline

    def to_user_score(self) -> UserScore:
        """Build a user score."""
        return UserScore(
            total_score=self.total_score,
            inbox_task_cnt=self.inbox_task_cnt,
            big_plan_cnt=self.big_plan_cnt,
        )

    def to_user_score_at_date(self) -> UserScoreAtDate:
        """Build a user score at time."""
        return UserScoreAtDate(
            date=ADate.from_date(self.created_time.as_date()),
            total_score=self.total_score,
            inbox_task_cnt=self.inbox_task_cnt,
            big_plan_cnt=self.big_plan_cnt,
        )


class ScoreStatsRepository(
    RecordRepository[ScoreStats, tuple[EntityId, RecurringTaskPeriod | None, str]],
    abc.ABC,
):
    """A repository of score stats."""

    @abc.abstractmethod
    async def find_all_in_timerange(
        self,
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod,
        start_date: ADate,
        end_date: ADate,
    ) -> list[ScoreStats]:
        """Find all score stats in a given time range."""
