"""The Notion connection."""
from dataclasses import dataclass

from jupiter.domain.remote.notion.space_id import NotionSpaceId
from jupiter.domain.remote.notion.token import NotionToken
from jupiter.framework.entity import Entity, FIRST_VERSION, StubEntity
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class NotionConnection(StubEntity):
    """The Notion connection."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class UpdateToken(Entity.Updated):
        """Updated access token."""

    workspace_ref_id: EntityId
    space_id: NotionSpaceId
    token: NotionToken

    @staticmethod
    def new_notion_connection(
            workspace_ref_id: EntityId, space_id: NotionSpaceId, token: NotionToken,
            source: EventSource, created_time: Timestamp) -> 'NotionConnection':
        """Create a Notion connection."""
        notion_connection = NotionConnection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[NotionConnection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            workspace_ref_id=workspace_ref_id,
            space_id=space_id,
            token=token)
        return notion_connection

    def update_token(self, token: NotionToken, source: EventSource, modification_time: Timestamp) -> 'NotionConnection':
        """Update the access token for the Notion connection."""
        return self._new_version(
            token=token,
            new_event=NotionConnection.UpdateToken.make_event_from_frame_args(source, self.version, modification_time))

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
