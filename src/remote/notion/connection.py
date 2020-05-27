"""The connection handles the lifetime of the interaction with Notion."""
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Optional, cast

import requests

from models.basic import WorkspaceSpaceId, WorkspaceToken
from remote.notion.client import NotionClient, NotionClientConfig
from utils.storage import StructuredIndividualStorage, JSONDictType


class MissingNotionConnectionError(Exception):
    """Error raised when there's no Notion connection data specified."""


class OldTokenForNotionConnectionError(Exception):
    """Error raised when the Notion connection's token has expired."""


@dataclass()
class NotionConnectionData:
    """Data about the link to Notion."""

    space_id: WorkspaceSpaceId
    token: WorkspaceToken


class NotionConnection:
    """The connection handles the lifetime of the interaction with Notion."""

    _NOTION_LINK_FILE_PATH: ClassVar[Path] = Path("/data/notion-connection.yaml")

    _structured_storage: Final[StructuredIndividualStorage[NotionConnectionData]]
    _cached_client: Optional[NotionClient]

    def __init__(self) -> None:
        """Constructor."""
        self._structured_storage = StructuredIndividualStorage(self._NOTION_LINK_FILE_PATH, self)
        self._cached_client = None

    def initialize(self, space_id: WorkspaceSpaceId, token: WorkspaceToken) -> None:
        """Initialize the Notion collection."""
        self._structured_storage.initialize(NotionConnectionData(space_id=space_id, token=token))

    def get_notion_client(self) -> NotionClient:
        """Construct a new Notion client."""
        if self._cached_client is not None:
            return self._cached_client

        notion_link = self._structured_storage.load_optional()

        if not notion_link:
            raise MissingNotionConnectionError()

        try:
            self._cached_client = NotionClient(NotionClientConfig(notion_link.space_id, notion_link.token))
            return self._cached_client
        except requests.exceptions.HTTPError as error:
            if str(error).find("Unauthorized for url"):
                raise OldTokenForNotionConnectionError()
            raise

    def update_token(self, new_token: WorkspaceToken) -> None:
        """Save new connection token."""
        data = self._structured_storage.load()
        data.token = new_token
        self._structured_storage.save(data)
        self._cached_client = None

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema of the data for this structure storage, as meant for basic storage."""
        return {
            "type": "object",
            "properties": {
                "space_id": {"type": "string"},
                "token": {"type": "string"}
            }
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> NotionConnectionData:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return NotionConnectionData(
            space_id=WorkspaceSpaceId(cast(str, storage_form["space_id"])),
            token=WorkspaceToken(cast(str, storage_form["token"])))

    @staticmethod
    def live_to_storage(live_form: NotionConnectionData) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "space_id": live_form.space_id,
            "token": live_form.token
        }
