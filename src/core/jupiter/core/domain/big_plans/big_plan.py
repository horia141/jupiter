"""A big plan."""
from typing import Optional

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
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
from jupiter.core.framework.update_action import UpdateAction


@entity
class BigPlan(LeafEntity):
    """A big plan."""

    big_plan_collection: ParentLink
    project_ref_id: EntityId
    name: BigPlanName
    status: BigPlanStatus
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None
    accepted_time: Optional[Timestamp] = None
    working_time: Optional[Timestamp] = None
    completed_time: Optional[Timestamp] = None

    inbox_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.BIG_PLAN, big_plan_ref_id=IsRefId()
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.BIG_PLAN, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_big_plan(
        ctx: DomainContext,
        big_plan_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: BigPlanName,
        status: BigPlanStatus,
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
    ) -> "BigPlan":
        """Create a big plan."""
        accepted_time = ctx.action_timestamp if status.is_accepted_or_more else None
        working_time = ctx.action_timestamp if status.is_working_or_more else None
        completed_time = ctx.action_timestamp if status.is_completed else None

        return BigPlan._create(
            ctx,
            big_plan_collection=ParentLink(big_plan_collection_ref_id),
            project_ref_id=project_ref_id,
            name=name,
            status=status,
            actionable_date=actionable_date,
            due_date=due_date,
            accepted_time=accepted_time,
            working_time=working_time,
            completed_time=completed_time,
        )

    @update_entity_action
    def change_project(
        self,
        ctx: DomainContext,
        project_ref_id: EntityId,
    ) -> "BigPlan":
        """Change the project for the inbox task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            ctx,
            project_ref_id=project_ref_id,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[BigPlanName],
        status: UpdateAction[BigPlanStatus],
        actionable_date: UpdateAction[Optional[ADate]],
        due_date: UpdateAction[Optional[ADate]],
    ) -> "BigPlan":
        """Update the big plan."""
        new_name = name.or_else(self.name)

        new_accepted_time = self.accepted_time
        new_working_time = self.working_time
        new_completed_time = self.completed_time
        if status.should_change:
            if (
                not self.status.is_accepted_or_more
                and status.just_the_value.is_accepted_or_more
            ):
                new_accepted_time = ctx.action_timestamp
            elif (
                self.status.is_accepted_or_more
                and not status.just_the_value.is_accepted_or_more
            ):
                new_accepted_time = None

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

        return self._new_version(
            ctx,
            name=new_name,
            status=new_status,
            accepted_time=new_accepted_time,
            working_time=new_working_time,
            completed_time=new_completed_time,
            actionable_date=new_actionable_date,
            due_date=new_due_date,
        )
