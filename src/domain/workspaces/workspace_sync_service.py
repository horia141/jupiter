"""The service class for syncing the Workspace."""
import logging
from typing import Final

from domain.sync_prefer import SyncPrefer
from domain.timestamp import Timestamp
from domain.workspaces.infra.workspace_engine import WorkspaceEngine
from domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from domain.workspaces.workspace import Workspace

LOGGER = logging.getLogger(__name__)


class WorkspaceSyncService:
    """The service class for syncing the Workspace."""

    _workspace_engine: Final[WorkspaceEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]

    def __init__(self, workspace_engine: WorkspaceEngine, workspace_notion_manager: WorkspaceNotionManager) -> None:
        """Constructor."""
        self._workspace_engine = workspace_engine
        self._workspace_notion_manager = workspace_notion_manager

    def sync(self, right_now: Timestamp, sync_prefer: SyncPrefer) -> Workspace:
        """Execute the service's action."""
        with self._workspace_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
        notion_workspace = self._workspace_notion_manager.load_workspace()

        if sync_prefer == SyncPrefer.NOTION:
            updated_workspace = notion_workspace.apply_to_aggregate_root(workspace, right_now)

            with self._workspace_engine.get_unit_of_work() as uow:
                uow.workspace_repository.save(updated_workspace)
            LOGGER.info("Changed workspace from Notion")
        elif sync_prefer == SyncPrefer.LOCAL:
            updated_notion_workspace = notion_workspace.join_with_aggregate_root(workspace)
            self._workspace_notion_manager.save_workspace(updated_notion_workspace)
            LOGGER.info("Applied changes on Notion side")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

        return workspace
