"""A inbox task collection."""
from dataclasses import dataclass

from framework.aggregate_root import AggregateRoot
from framework.base.entity_id import EntityId, BAD_REF_ID
from framework.base.timestamp import Timestamp


@dataclass()
class InboxTaskCollection(AggregateRoot):
    """A inbox task collection."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    _project_ref_id: EntityId

    @staticmethod
    def new_inbox_task_collection(project_ref_id: EntityId, created_time: Timestamp) -> 'InboxTaskCollection':
        """Create a inbox task collection."""
        inbox_task_collection = InboxTaskCollection(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _project_ref_id=project_ref_id)
        inbox_task_collection.record_event(InboxTaskCollection.Created.make_event_from_frame_args(created_time))

        return inbox_task_collection

    @property
    def project_ref_id(self) -> EntityId:
        """The project which owns this collection."""
        return self._project_ref_id
