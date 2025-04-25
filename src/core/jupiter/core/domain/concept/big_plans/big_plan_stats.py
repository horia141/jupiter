"""Stats about a big plan."""

import abc

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.record import Record, create_record_action, record
from jupiter.core.framework.repository import RecordRepository


@record
class BigPlanStats(Record):
    """Stats about a big plan."""

    big_plan: ParentLink
    all_inbox_tasks_cnt: int
    completed_inbox_tasks_cnt: int

    @staticmethod
    @create_record_action
    def new_stats(ctx: DomainContext, big_plan_ref_id: EntityId) -> "BigPlanStats":
        """Create a new big plan stats."""
        return BigPlanStats._create(
            ctx,
            big_plan=ParentLink(big_plan_ref_id),
            all_inbox_tasks_cnt=0,
            completed_inbox_tasks_cnt=0,
        )

    @staticmethod
    @create_record_action
    def new_stats_for_big_plan(
        ctx: DomainContext,
        big_plan_ref_id: EntityId,
        all_inbox_tasks_cnt: int,
        completed_inbox_tasks_cnt: int,
    ) -> "BigPlanStats":
        """Create a new big plan stats for a big plan."""
        if all_inbox_tasks_cnt < 0:
            raise InputValidationError("Cannot have negative inbox tasks counts")
        if completed_inbox_tasks_cnt < 0:
            raise InputValidationError("Cannot have negative completed inbox tasks")
        if completed_inbox_tasks_cnt > all_inbox_tasks_cnt:
            raise InputValidationError(
                "Cannot have more done inbox tasks than all inbox taks"
            )
        return BigPlanStats._create(
            ctx,
            big_plan=ParentLink(big_plan_ref_id),
            all_inbox_tasks_cnt=all_inbox_tasks_cnt,
            completed_inbox_tasks_cnt=completed_inbox_tasks_cnt,
        )

    @property
    def raw_key(self) -> object:
        """The raw key of the big plan stats."""
        return self.big_plan.ref_id


class BigPlanStatsRepository(RecordRepository[BigPlanStats, EntityId], abc.ABC):
    """A repository of big plan stats."""

    @abc.abstractmethod
    async def mark_add_inbox_task(self, big_plan_ref_id: EntityId) -> None:
        """Mark that a new inbox task has been added to the big plan."""

    @abc.abstractmethod
    async def mark_remove_inbox_task(
        self, big_plan_ref_id: EntityId, is_completed: bool
    ) -> None:
        """Mark that an inbox task has been removed from the big plan."""

    @abc.abstractmethod
    async def mark_inbox_task_done(self, big_plan_ref_id: EntityId) -> None:
        """Mark that an inbox task has been done on the big plan."""

    @abc.abstractmethod
    async def mark_inbox_task_undone(self, big_plan_ref_id: EntityId) -> None:
        """Mark that an inbox task has been undone on the big plan."""
