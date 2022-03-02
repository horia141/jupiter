"""A big plan collection."""
from dataclasses import dataclass

from jupiter.framework.entity import Entity, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class BigPlanCollection(Entity):
    """A big plan collection."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    workspace_ref_id: EntityId

    @staticmethod
    def new_big_plan_collection(
            workspace_ref_id: EntityId, source: EventSource, created_time: Timestamp) -> 'BigPlanCollection':
        """Create a big plan collection."""
        big_plan_collection = BigPlanCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[BigPlanCollection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            workspace_ref_id=workspace_ref_id)
        return big_plan_collection
