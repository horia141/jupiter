"""A big plan."""
import uuid
from dataclasses import dataclass
from typing import Optional

from domain.adate import ADate
from domain.big_plans.big_plan_status import BigPlanStatus
from domain.entity_name import EntityName
from domain.timestamp import Timestamp
from models.framework import AggregateRoot, EntityId, BAD_REF_ID, UpdateAction, Event2


@dataclass()
class BigPlan(AggregateRoot):
    """A big plan."""

    @dataclass(frozen=True)
    class Created(Event2):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Event2):
        """Updated event."""

    _big_plan_collection_ref_id: EntityId
    _name: EntityName
    _status: BigPlanStatus
    _due_date: Optional[ADate]
    _notion_link_uuid: uuid.UUID
    _accepted_time: Optional[Timestamp]
    _working_time: Optional[Timestamp]
    _completed_time: Optional[Timestamp]

    @staticmethod
    def new_big_plan(
            archived: bool, big_plan_collection_ref_id: EntityId, name: EntityName, status: BigPlanStatus,
            due_date: Optional[ADate], created_time: Timestamp) -> 'BigPlan':
        """Create a big plan."""
        big_plan = BigPlan(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _big_plan_collection_ref_id=big_plan_collection_ref_id,
            _name=name,
            _status=status,
            _due_date=due_date,
            _notion_link_uuid=uuid.uuid4(),
            _accepted_time=created_time if status.is_accepted_or_more else None,
            _working_time=created_time if status.is_working_or_more else None,
            _completed_time=created_time if status.is_completed else None)
        big_plan.record_event(Event2.make_event_from_frame_args(BigPlan.Created, created_time))

        return big_plan

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'BigPlan':
        """Change the name of the big plan."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Event2.make_event_from_frame_args(BigPlan.Updated, modification_time))
        return self

    def change_status(self, status: BigPlanStatus, modification_time: Timestamp) -> 'BigPlan':
        """Change the status of the big plan."""
        if self._status == status:
            return self

        updated_accepted_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_accepted_or_more and status.is_accepted_or_more:
            self._accepted_time = modification_time
            updated_accepted_time = UpdateAction.change_to(modification_time)
        elif self._status.is_accepted_or_more and not status.is_accepted_or_more:
            self._accepted_time = None
            updated_accepted_time = UpdateAction.change_to(None)
        else:
            updated_accepted_time = UpdateAction.do_nothing()

        updated_working_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_working_or_more and status.is_working_or_more:
            self._working_time = modification_time
            updated_working_time = UpdateAction.change_to(modification_time)
        elif self._status.is_working_or_more and not status.is_working_or_more:
            self._working_time = None
            updated_working_time = UpdateAction.change_to(None)
        else:
            updated_working_time = UpdateAction.do_nothing()

        updated_completed_time: UpdateAction[Optional[Timestamp]]
        if not self._status.is_completed and status.is_completed:
            self._completed_time = modification_time
            updated_completed_time = UpdateAction.change_to(modification_time)
        elif self._status.is_completed and not status.is_completed:
            self._completed_time = None
            updated_completed_time = UpdateAction.change_to(None)
        else:
            updated_completed_time = UpdateAction.do_nothing()
        self._status = status
        self.record_event(Event2.make_event_from_frame_args(
            BigPlan.Updated, modification_time, updated_accepted_time=updated_accepted_time,
            updated_working_time=updated_working_time, updated_completed_time=updated_completed_time))
        return self

    def change_due_date(self, due_date: Optional[ADate], modification_time: Timestamp) -> 'BigPlan':
        """Change the due date of the big plan."""
        if self._due_date == due_date:
            return self
        self._due_date = due_date
        self.record_event(Event2.make_event_from_frame_args(BigPlan.Updated, modification_time))
        return self

    @property
    def project_ref_id(self) -> EntityId:
        """The id of the project this big plan belongs to."""
        # TODO(horia141): fix this uglyness
        return self._big_plan_collection_ref_id

    @property
    def big_plan_collection_ref_id(self) -> EntityId:
        """The big plan collection this big plan belongs to."""
        return self._big_plan_collection_ref_id

    @property
    def name(self) -> EntityName:
        """The name of the big plan."""
        return self._name

    @property
    def status(self) -> BigPlanStatus:
        """The status of the big plan."""
        return self._status

    @property
    def due_date(self) -> Optional[ADate]:
        """The due date of the big plan."""
        return self._due_date

    @property
    def notion_link_uuid(self) -> uuid.UUID:
        """A stable Notion link for the big plan."""
        return self._notion_link_uuid

    @property
    def accepted_time(self) -> Optional[Timestamp]:
        """The time when the big plan was accepted for work."""
        return self._accepted_time

    @property
    def working_time(self) -> Optional[Timestamp]:
        """The time when work begun on the big plan."""
        return self._working_time

    @property
    def completed_time(self) -> Optional[Timestamp]:
        """The time when the big plan was completed."""
        return self._completed_time
