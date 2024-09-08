"""The best score for a period of time and a particular subdivision of it."""
import abc

from jupiter.core.domain.application.gamification.score_stats import ScoreStats
from jupiter.core.domain.application.gamification.user_score_overview import UserScore
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.record import (
    Record,
    create_record_action,
    record,
    update_record_action,
)
from jupiter.core.framework.repository import RecordRepository


@record
class ScorePeriodBest(Record):
    """The best score for a period of time and a particular subdivision of it."""

    score_log: ParentLink
    period: RecurringTaskPeriod | None
    timeline: str
    sub_period: RecurringTaskPeriod
    total_score: int
    inbox_task_cnt: int
    big_plan_cnt: int

    @staticmethod
    @create_record_action
    def new_score_period_best(
        ctx: DomainContext,
        score_log_ref_id: EntityId,
        period: RecurringTaskPeriod | None,
        timeline: str,
        sub_period: RecurringTaskPeriod,
    ) -> "ScorePeriodBest":
        """Create a score period best for a given period and timeline."""
        if period is not None:
            if period < sub_period:
                raise InputValidationError(
                    f"period {period} cannot be less than sub_period {sub_period}"
                )

        return ScorePeriodBest._create(
            ctx,
            score_log=ParentLink(score_log_ref_id),
            period=period,
            timeline=timeline,
            sub_period=sub_period,
            total_score=0,
            inbox_task_cnt=0,
            big_plan_cnt=0,
        )

    @update_record_action
    def update_to_max(
        self, ctx: DomainContext, score_stats: ScoreStats
    ) -> "ScorePeriodBest":
        """Update the score period best to the maximum of the two."""
        return self._new_version(
            ctx,
            total_score=max(self.total_score, score_stats.total_score),
            inbox_task_cnt=self.inbox_task_cnt
            if self.total_score > score_stats.total_score
            else score_stats.inbox_task_cnt,
            big_plan_cnt=self.big_plan_cnt
            if self.total_score > score_stats.total_score
            else score_stats.big_plan_cnt,
        )

    @property
    def raw_key(self) -> object:
        """The raw key of the score best."""
        return self.key

    @property
    def key(
        self,
    ) -> tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod]:
        """The key of the score best."""
        return self.score_log.ref_id, self.period, self.timeline, self.sub_period

    def to_user_score(self) -> UserScore:
        """Build a user score."""
        return UserScore(
            total_score=self.total_score,
            inbox_task_cnt=self.inbox_task_cnt,
            big_plan_cnt=self.big_plan_cnt,
        )


class ScorePeriodBestRepository(
    RecordRepository[
        ScorePeriodBest,
        tuple[EntityId, RecurringTaskPeriod | None, str, RecurringTaskPeriod],
    ],
    abc.ABC,
):
    """A repository of score period bests."""
