"""The builder is in charge of managing the lifetime of the Notion client."""
from typing import Final, Optional

import requests

from jupiter.domain.remote.notion.connection_repository import (
    NotionConnectionNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.remote.notion.infra.client import NotionClient, NotionClientConfig
from jupiter.remote.notion.infra.client_v2 import NotionClientV2, NotionClientV2Config


class MissingNotionConnectionError(Exception):
    """Error raised when there's no Notion connection data specified."""


class OldTokenForNotionConnectionError(Exception):
    """Error raised when the Notion connection's token has expired."""


class NotionClientBuilder:
    """The builder is in charge of managing the lifetime of the Notion client."""

    _storage_engine: Final[DomainStorageEngine]
    _cached_client: Optional[NotionClient]
    _cached_client_v2: Optional[NotionClientV2]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._cached_client = None
        self._cached_client_v2 = None

    def get_notion_client(self) -> NotionClient:
        """Construct a new Notion client."""
        if self._cached_client is not None:
            return self._cached_client

        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            try:
                notion_connection = uow.notion_connection_repository.load_by_parent(
                    workspace.ref_id
                )
            except NotionConnectionNotFoundError as err:
                raise MissingNotionConnectionError() from err

        try:
            self._cached_client = NotionClient(
                NotionClientConfig(notion_connection.space_id, notion_connection.token)
            )
            return self._cached_client
        except requests.exceptions.HTTPError as error:
            if str(error).find("Unauthorized for url"):
                raise OldTokenForNotionConnectionError() from error
            raise

    def get_notion_client_v2(self) -> NotionClientV2:
        """Construct a new Notion client."""
        if self._cached_client_v2 is not None:
            return self._cached_client_v2

        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            try:
                notion_connection = uow.notion_connection_repository.load_by_parent(
                    workspace.ref_id
                )
            except NotionConnectionNotFoundError as err:
                raise MissingNotionConnectionError() from err

        self._cached_client_v2 = NotionClientV2(
            NotionClientV2Config(notion_connection.api_token)
        )
        return self._cached_client_v2
