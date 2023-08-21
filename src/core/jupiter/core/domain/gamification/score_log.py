"""A container for all the scores a user has."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, TrunkEntity
from jupiter.core.framework.event import EventSource


@dataclass
class ScoreLog(TrunkEntity):
    """a log of the scores a user receives."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    user_ref_id: EntityId

    @staticmethod
    def new_score_log(
        user_ref_id: EntityId, source: EventSource, created_time: Timestamp
    ) -> "ScoreLog":
        """Create a score log for a user."""
        score_log = ScoreLog(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                ScoreLog.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            user_ref_id=user_ref_id,
        )
        return score_log
