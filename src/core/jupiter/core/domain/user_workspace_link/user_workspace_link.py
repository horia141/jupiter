"""A 1:1 link between users and workspaces."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, RootEntity
from jupiter.core.framework.event import EventSource


@dataclass
class UserWorkspaceLink(RootEntity):
    """A 1:1 link between a user and a workspace."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    user_ref_id: EntityId
    workspace_ref_id: EntityId

    @staticmethod
    def new_user_workspace_link(
        user_ref_id: EntityId,
        workspace_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "UserWorkspaceLink":
        """Create a new user workspace link."""
        user_workspace_link = UserWorkspaceLink(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            last_modified_time=created_time,
            archived_time=None,
            events=[
                UserWorkspaceLink.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                ),
            ],
            user_ref_id=user_ref_id,
            workspace_ref_id=workspace_ref_id,
        )

        return user_workspace_link
