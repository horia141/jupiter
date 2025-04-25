"""A big plan."""

import abc
from typing import Iterable

from jupiter.core.domain.concept.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.concept.big_plans.big_plan_stats import BigPlanStats
from jupiter.core.domain.concept.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.concept.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.record import ContainsOneRecord
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction


@entity
class BigPlan(LeafEntity):
    """A big plan."""

    big_plan_collection: ParentLink
    project_ref_id: EntityId
    name: BigPlanName
    status: BigPlanStatus
    eisen: Eisen
    difficulty: Difficulty
    actionable_date: ADate | None
    due_date: ADate | None
    working_time: Timestamp | None
    completed_time: Timestamp | None

    inbox_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.BIG_PLAN, source_entity_ref_id=IsRefId()
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.BIG_PLAN, source_entity_ref_id=IsRefId()
    )
    stats = ContainsOneRecord(BigPlanStats, big_plan_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_big_plan(
        ctx: DomainContext,
        big_plan_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: BigPlanName,
        status: BigPlanStatus,
        eisen: Eisen,
        difficulty: Difficulty,
        actionable_date: ADate | None,
        due_date: ADate | None,
    ) -> "BigPlan":
        """Create a big plan."""
        BigPlan._check_actionable_and_due_dates(actionable_date, due_date)
        working_time = ctx.action_timestamp if status.is_working_or_more else None
        completed_time = ctx.action_timestamp if status.is_completed else None

        return BigPlan._create(
            ctx,
            big_plan_collection=ParentLink(big_plan_collection_ref_id),
            project_ref_id=project_ref_id,
            name=name,
            status=status,
            eisen=eisen,
            difficulty=difficulty,
            actionable_date=actionable_date,
            due_date=due_date,
            working_time=working_time,
            completed_time=completed_time,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[BigPlanName],
        status: UpdateAction[BigPlanStatus],
        project_ref_id: UpdateAction[EntityId],
        eisen: UpdateAction[Eisen],
        difficulty: UpdateAction[Difficulty],
        actionable_date: UpdateAction[ADate | None],
        due_date: UpdateAction[ADate | None],
    ) -> "BigPlan":
        """Update the big plan."""
        BigPlan._check_actionable_and_due_dates(
            actionable_date.or_else(self.actionable_date),
            due_date.or_else(self.due_date),
        )
        new_name = name.or_else(self.name)

        new_working_time = self.working_time
        new_completed_time = self.completed_time
        if status.should_change:
            if (
                not self.status.is_working_or_more
                and status.just_the_value.is_working_or_more
            ):
                new_working_time = ctx.action_timestamp
            elif (
                self.status.is_working_or_more
                and not status.just_the_value.is_working_or_more
            ):
                new_working_time = None

            if not self.status.is_completed and status.just_the_value.is_completed:
                new_completed_time = ctx.action_timestamp
            elif self.status.is_completed and not status.just_the_value.is_completed:
                new_completed_time = None
            new_status = status.just_the_value
        else:
            new_status = self.status

        new_actionable_date = actionable_date.or_else(self.actionable_date)
        new_due_date = due_date.or_else(self.due_date)
        new_eisen = eisen.or_else(self.eisen)
        new_difficulty = difficulty.or_else(self.difficulty)

        return self._new_version(
            ctx,
            name=new_name,
            status=new_status,
            project_ref_id=project_ref_id.or_else(self.project_ref_id),
            eisen=new_eisen,
            difficulty=new_difficulty,
            working_time=new_working_time,
            completed_time=new_completed_time,
            actionable_date=new_actionable_date,
            due_date=new_due_date,
        )

    @update_entity_action
    def change_dates_via_time_plan(
        self,
        ctx: DomainContext,
        actionable_date: ADate,
        due_date: ADate,
    ) -> "BigPlan":
        """Update the inbox task."""
        self._check_actionable_and_due_dates(actionable_date, due_date)

        return self._new_version(
            ctx, actionable_date=actionable_date, due_date=due_date
        )

    @property
    def is_working(self) -> bool:
        """Whether this task is being worked on or not."""
        return self.status.is_working

    @property
    def is_working_or_more(self) -> bool:
        """Whether this task is being worked on or not."""
        return self.status.is_working_or_more

    @property
    def is_completed(self) -> bool:
        """Whether the big plan is completed or not."""
        return self.status.is_completed

    @staticmethod
    def _check_actionable_and_due_dates(
        actionable_date: ADate | None,
        due_date: ADate | None,
    ) -> None:
        if actionable_date is None or due_date is None:
            return

        if actionable_date > due_date:
            raise InputValidationError(
                f"The actionable date {actionable_date} should be before the due date {due_date}",
            )


class BigPlanRepository(LeafEntityRepository[BigPlan], abc.ABC):
    """A repository of big plans."""

    @abc.abstractmethod
    async def find_completed_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason],
        filter_start_completed_date: ADate,
        filter_end_completed_date: ADate,
        filter_exclude_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[BigPlan]:
        """Find all completed big plans in a time range."""
