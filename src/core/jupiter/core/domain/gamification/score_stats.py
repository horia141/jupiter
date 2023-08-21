"""Statistics about scores for a particular time interval."""
from dataclasses import dataclass
from typing import Tuple

from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import Record
from jupiter.core.framework.event import EventSource


@dataclass
class ScoreStats(Record):
    """Statistics about scores for a particular time interval."""

    score_log_ref_id: EntityId
    period: RecurringTaskPeriod | None
    timeline: str
    total_score: int

    @staticmethod
    def new_score_stats(
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod | None,
        timeline: str,
        created_time: Timestamp,
    ) -> "ScoreStats":
        """Create a score stats for a given period and timeline."""
        score_stats = ScoreStats(
            created_time=created_time,
            last_modified_time=created_time,
            score_log_ref_id=score_log_ref_id,
            period=period,
            timeline=timeline,
            total_score=0,
        )
        return score_stats

    def merge_score(
        self,
        score_log_entry: ScoreLogEntry,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "ScoreStats":
        return self._new_version(
            last_modified_time=modification_time,
            total_score=max(0, self.total_score + score_log_entry.score),
        )

    @property
    def key(self) -> Tuple[EntityId, RecurringTaskPeriod | None, str]:
        """The key of the score stats."""
        return self.score_log_ref_id, self.period, self.timeline
