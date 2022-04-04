"""The service class for dealing with chores."""
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.chore_collection import ChoreCollection
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import (
    NotionInboxTaskCollection,
)
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class ChoreSyncService(
    TrunkLeafNotionSyncService[
        ChoreCollection,
        Chore,
        NotionWorkspace,
        NotionChoreCollection,
        NotionChore,
        NotionInboxTaskCollection,
        NotionChore.DirectInfo,
        NotionChore.InverseInfo,
    ]
):
    """The service class for dealing with chores."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        chore_notion_manager: ChoreNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            ChoreCollection, Chore, NotionChore, storage_engine, chore_notion_manager
        )
