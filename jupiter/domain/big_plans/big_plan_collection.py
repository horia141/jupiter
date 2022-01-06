"""A big plan collection."""
from dataclasses import dataclass

from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp


@dataclass()
class BigPlanCollection(AggregateRoot):
    """A big plan collection."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    project_ref_id: EntityId

    @staticmethod
    def new_big_plan_collection(project_ref_id: EntityId, created_time: Timestamp) -> 'BigPlanCollection':
        """Create a big plan collection."""
        big_plan_collection = BigPlanCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            project_ref_id=project_ref_id)
        big_plan_collection.record_event(BigPlanCollection.Created.make_event_from_frame_args(created_time))

        return big_plan_collection
