"""A inbox task collection."""
from dataclasses import dataclass

from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class InboxTaskCollection(AggregateRoot):
    """A inbox task collection."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    project_ref_id: EntityId

    @staticmethod
    def new_inbox_task_collection(
            project_ref_id: EntityId, source: EventSource, created_time: Timestamp) -> 'InboxTaskCollection':
        """Create a inbox task collection."""
        inbox_task_collection = InboxTaskCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[InboxTaskCollection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            project_ref_id=project_ref_id)
        return inbox_task_collection
