"""The service class for syncing the Workspace."""
import logging
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.timestamp import Timestamp

LOGGER = logging.getLogger(__name__)


class WorkspaceSyncService:
    """The service class for syncing the Workspace."""

    _storage_engine: Final[DomainStorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]

    def __init__(self, storage_engine: DomainStorageEngine, workspace_notion_manager: WorkspaceNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager

    def sync(self, right_now: Timestamp, sync_prefer: SyncPrefer) -> Workspace:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()
        notion_workspace = self._workspace_notion_manager.load_workspace(workspace.ref_id)

        if sync_prefer == SyncPrefer.NOTION:
            workspace = notion_workspace.apply_to_aggregate_root(workspace, right_now)

            with self._storage_engine.get_unit_of_work() as uow:
                uow.workspace_repository.save(workspace)
            LOGGER.info("Changed workspace from Notion")
        elif sync_prefer == SyncPrefer.LOCAL:
            notion_workspace = notion_workspace.join_with_aggregate_root(workspace)
            self._workspace_notion_manager.save_workspace(notion_workspace)
            LOGGER.info("Applied changes on Notion side")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

        return workspace
