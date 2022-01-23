"""Usecase for updating a Notion connection token."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.remote.notion.token import NotionToken
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class NotionConnectionUpdateTokenUseCase(UseCase['NotionConnectionUpdateTokenUseCase.Args', None]):
    """UseCase for updating a workspace."""

    @dataclass()
    class Args:
        """Args."""
        token: NotionToken

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
            notion_connection = uow.notion_connection_repository.load_for_workspace(workspace.ref_id)
            notion_connection = \
                notion_connection.update_token(args.token, EventSource.CLI, self._time_provider.get_current_time())
            uow.notion_connection_repository.save(notion_connection)
