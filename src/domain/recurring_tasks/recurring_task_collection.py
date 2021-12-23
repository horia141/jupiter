"""A recurring task collection."""
from dataclasses import dataclass

from framework.base.timestamp import Timestamp
from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId, BAD_REF_ID
from framework.event import Event2


@dataclass()
class RecurringTaskCollection(AggregateRoot):
    """A recurring task collection."""

    @dataclass(frozen=True)
    class Created(Event2):
        """Created event."""

    _project_ref_id: EntityId

    @staticmethod
    def new_recurring_task_collection(project_ref_id: EntityId, created_time: Timestamp) -> 'RecurringTaskCollection':
        """Create a recurring task collection."""
        recurring_task_collection = RecurringTaskCollection(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _project_ref_id=project_ref_id)
        recurring_task_collection.record_event(
            Event2.make_event_from_frame_args(RecurringTaskCollection.Created, created_time))

        return recurring_task_collection

    @property
    def project_ref_id(self) -> EntityId:
        """The project which owns this collection."""
        return self._project_ref_id
