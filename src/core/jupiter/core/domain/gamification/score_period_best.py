"""The best score for a period of time and a particular subdivision of it."""
from dataclasses import dataclass
from typing import Tuple

from jupiter.core.domain.gamification.score_stats import ScoreStats
from jupiter.core.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import Record
from jupiter.core.framework.errors import InputValidationError


@dataclass
class ScorePeriodBest(Record):
    """The best score for a period of time and a particular subdivision of it."""

    score_log_ref_id: EntityId
    period: RecurringTaskPeriod | None
    timeline: str
    sub_period: RecurringTaskPeriod
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int

    @staticmethod
    def new_score_period_best(
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod | None,
        timeline: str,
        sub_period: RecurringTaskPeriod,
        created_time: Timestamp,
    ) -> "ScorePeriodBest":
        """Create a score period best for a given period and timeline."""
        if period is not None:
            if period < sub_period:
                raise InputValidationError(
                    f"period {period} cannot be less than sub_period {sub_period}"
                )

        score_period_best = ScorePeriodBest(
            created_time=created_time,
            last_modified_time=created_time,
            score_log_ref_id=score_log_ref_id,
            period=period,
            timeline=timeline,
            sub_period=sub_period,
            total_score=0,
            inbox_task_cnt=0,
            big_plan_cnt=0,
        )
        return score_period_best

    def update_to_max(
        self, score_stats: ScoreStats, modification_time: Timestamp
    ) -> "ScorePeriodBest":
        return self._new_version(
            last_modified_time=modification_time,
            total_score=max(self.total_score, score_stats.total_score),
            inbox_task_cnt=self.inbox_task_cnt if self.total_score > score_stats.total_score else score_stats.inbox_task_cnt,
            big_plan_cnt=self.big_plan_cnt if self.total_score > score_stats.total_score else score_stats.big_plan_cnt,
        )

    @property
    def key(
        self,
    ) -> Tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod]:
        """The key of the score best."""
        return self.score_log_ref_id, self.period, self.timeline, self.sub_period
