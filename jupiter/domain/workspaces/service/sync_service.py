"""The service class for syncing the Workspace."""
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.infra.workspace_notion_manager import (
    WorkspaceNotionManager,
)
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.use_case import ProgressReporter


class WorkspaceSyncService:
    """The service class for syncing the Workspace."""

    _storage_engine: Final[DomainStorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        workspace_notion_manager: WorkspaceNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager

    def sync(
        self,
        progress_reporter: ProgressReporter,
        right_now: Timestamp,
        sync_prefer: SyncPrefer,
    ) -> Workspace:
        """Execute the service's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            workspace = uow.workspace_repository.load()

        with progress_reporter.start_updating_entity(
            "workspace", workspace.ref_id, str(workspace.name)
        ) as entity_reporter:
            notion_workspace = self._workspace_notion_manager.load_workspace(
                workspace.ref_id
            )

            if sync_prefer == SyncPrefer.NOTION:
                new_workspace = notion_workspace.apply_to_entity(workspace, right_now)

                if new_workspace != workspace:
                    with self._storage_engine.get_unit_of_work() as uow:
                        workspace = uow.workspace_repository.save(new_workspace)
                    entity_reporter.mark_known_name(
                        str(workspace.name)
                    ).mark_local_change()
                else:
                    entity_reporter.mark_not_needed()
            elif sync_prefer == SyncPrefer.LOCAL:
                notion_workspace = notion_workspace.join_with_entity(workspace)
                self._workspace_notion_manager.save_workspace(notion_workspace)
                entity_reporter.mark_remote_change()
            else:
                raise Exception(f"Invalid preference {sync_prefer}")

        return workspace
