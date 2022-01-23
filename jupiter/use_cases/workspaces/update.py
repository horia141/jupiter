"""UseCase for updating a workspace."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class WorkspaceUpdateUseCase(UseCase['WorkspaceUpdateUseCase.Args', None]):
    """UseCase for updating a workspace."""

    @dataclass()
    class Args:
        """Args."""
        name: UpdateAction[WorkspaceName]
        timezone: UpdateAction[Timezone]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            workspace_notion_manager: WorkspaceNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

            workspace = workspace.update(
                name=args.name, timezone=args.timezone,
                source=EventSource.CLI, modification_time=self._time_provider.get_current_time())

            uow.workspace_repository.save(workspace)

        notion_workspace = self._workspace_notion_manager.load_workspace(workspace.ref_id)
        notion_workspace = notion_workspace.join_with_aggregate_root(workspace)
        self._workspace_notion_manager.save_workspace(notion_workspace)
