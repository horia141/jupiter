"""A big plan."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class BigPlan(LeafEntity):
    """A big plan."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class ChangeProject(Entity.Updated):
        """Changed the project event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    big_plan_collection_ref_id: EntityId
    project_ref_id: EntityId
    name: BigPlanName
    status: BigPlanStatus
    actionable_date: Optional[ADate] = None
    due_date: Optional[ADate] = None
    accepted_time: Optional[Timestamp] = None
    working_time: Optional[Timestamp] = None
    completed_time: Optional[Timestamp] = None

    @staticmethod
    def new_big_plan(
        archived: bool,
        big_plan_collection_ref_id: EntityId,
        project_ref_id: EntityId,
        name: BigPlanName,
        status: BigPlanStatus,
        actionable_date: Optional[ADate],
        due_date: Optional[ADate],
        source: EventSource,
        created_time: Timestamp,
    ) -> "BigPlan":
        """Create a big plan."""
        accepted_time = created_time if status.is_accepted_or_more else None
        working_time = created_time if status.is_working_or_more else None
        completed_time = created_time if status.is_completed else None

        big_plan = BigPlan(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=archived,
            created_time=created_time,
            archived_time=created_time if archived else None,
            last_modified_time=created_time,
            events=[
                BigPlan.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                    accepted_time=accepted_time,
                    working_time=working_time,
                    completed_time=completed_time,
                ),
            ],
            big_plan_collection_ref_id=big_plan_collection_ref_id,
            project_ref_id=project_ref_id,
            name=name,
            status=status,
            actionable_date=actionable_date,
            due_date=due_date,
            accepted_time=accepted_time,
            working_time=working_time,
            completed_time=completed_time,
        )
        return big_plan

    def change_project(
        self,
        project_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "BigPlan":
        """Change the project for the inbox task."""
        if self.project_ref_id == project_ref_id:
            return self
        return self._new_version(
            project_ref_id=project_ref_id,
            new_event=BigPlan.ChangeProject.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def update(
        self,
        name: UpdateAction[BigPlanName],
        status: UpdateAction[BigPlanStatus],
        actionable_date: UpdateAction[Optional[ADate]],
        due_date: UpdateAction[Optional[ADate]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "BigPlan":
        """Update the big plan."""
        new_name = name.or_else(self.name)

        new_accepted_time = self.accepted_time
        new_working_time = self.working_time
        new_completed_time = self.completed_time
        if status.should_change:
            updated_accepted_time: UpdateAction[Optional[Timestamp]]
            if (
                not self.status.is_accepted_or_more
                and status.just_the_value.is_accepted_or_more
            ):
                new_accepted_time = modification_time
                updated_accepted_time = UpdateAction.change_to(modification_time)
            elif (
                self.status.is_accepted_or_more
                and not status.just_the_value.is_accepted_or_more
            ):
                new_accepted_time = None
                updated_accepted_time = UpdateAction.change_to(None)
            else:
                updated_accepted_time = UpdateAction.do_nothing()

            updated_working_time: UpdateAction[Optional[Timestamp]]
            if (
                not self.status.is_working_or_more
                and status.just_the_value.is_working_or_more
            ):
                new_working_time = modification_time
                updated_working_time = UpdateAction.change_to(modification_time)
            elif (
                self.status.is_working_or_more
                and not status.just_the_value.is_working_or_more
            ):
                new_working_time = None
                updated_working_time = UpdateAction.change_to(None)
            else:
                updated_working_time = UpdateAction.do_nothing()

            updated_completed_time: UpdateAction[Optional[Timestamp]]
            if not self.status.is_completed and status.just_the_value.is_completed:
                new_completed_time = modification_time
                updated_completed_time = UpdateAction.change_to(modification_time)
            elif self.status.is_completed and not status.just_the_value.is_completed:
                new_completed_time = None
                updated_completed_time = UpdateAction.change_to(None)
            else:
                updated_completed_time = UpdateAction.do_nothing()
            new_status = status.just_the_value

            event_kwargs = {
                "updated_accepted_time": updated_accepted_time,
                "updated_working_time": updated_working_time,
                "updated_completed_time": updated_completed_time,
            }
        else:
            event_kwargs = {}
            new_status = self.status

        new_actionable_date = actionable_date.or_else(self.actionable_date)
        new_due_date = due_date.or_else(self.due_date)

        return self._new_version(
            name=new_name,
            status=new_status,
            accepted_time=new_accepted_time,
            working_time=new_working_time,
            completed_time=new_completed_time,
            actionable_date=new_actionable_date,
            due_date=new_due_date,
            new_event=BigPlan.Updated.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
                **event_kwargs,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.big_plan_collection_ref_id
