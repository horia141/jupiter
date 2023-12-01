"""A task generation log attched to a workspace."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, TrunkEntity
from jupiter.core.framework.event import EventSource


@dataclass
class GenLog(TrunkEntity):
    """A log of task generation actions a user has performed."""

    @dataclass
    class Created(Entity.Created):
        """Event that gets triggered when a Gen log is created."""

    workspace_ref_id: EntityId

    @staticmethod
    def new_gen_log(
        workspace_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "GenLog":
        """Create a new Gen log."""
        score_log = GenLog(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                GenLog.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            workspace_ref_id=workspace_ref_id,
        )
        return score_log
