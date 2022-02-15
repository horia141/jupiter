"""A chore collection."""
from dataclasses import dataclass

from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class ChoreCollection(AggregateRoot):
    """A chore collection."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    workspace_ref_id: EntityId

    @staticmethod
    def new_chore_collection(
            workspace_ref_id: EntityId, source: EventSource, created_time: Timestamp) -> 'ChoreCollection':
        """Create a chore collection."""
        chore_collection = ChoreCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[ChoreCollection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            workspace_ref_id=workspace_ref_id)
        return chore_collection
