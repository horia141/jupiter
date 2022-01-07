"""A recurring task collection."""
from dataclasses import dataclass

from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass()
class RecurringTaskCollection(AggregateRoot):
    """A recurring task collection."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    project_ref_id: EntityId

    @staticmethod
    def new_recurring_task_collection(
            project_ref_id: EntityId, source: EventSource, created_time: Timestamp) -> 'RecurringTaskCollection':
        """Create a recurring task collection."""
        recurring_task_collection = RecurringTaskCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            project_ref_id=project_ref_id)
        recurring_task_collection.record_event(
            RecurringTaskCollection.Created.make_event_from_frame_args(
                source, recurring_task_collection.version, created_time))

        return recurring_task_collection
