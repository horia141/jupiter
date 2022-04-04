"""A container for all the group of various push integrations we have."""
from dataclasses import dataclass

from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import TrunkEntity, Entity, FIRST_VERSION
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class PushIntegrationGroup(TrunkEntity):
    """A container for all the group of various push integrations we have."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    workspace_ref_id: EntityId

    @staticmethod
    def new_push_integration_group(
        workspace_ref_id: EntityId, source: EventSource, created_time: Timestamp
    ) -> "PushIntegrationGroup":
        """Create a habit collection."""
        push_integration_group = PushIntegrationGroup(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                PushIntegrationGroup.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                )
            ],
            workspace_ref_id=workspace_ref_id,
        )
        return push_integration_group

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent entity id."""
        return self.workspace_ref_id
