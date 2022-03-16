"""The service class for syncing inbox tasks."""
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.notion_sync_service import TrunkLeafNotionSyncService
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class InboxTaskSyncService(
    TrunkLeafNotionSyncService[
        InboxTaskCollection,
        InboxTask,
        NotionWorkspace,
        NotionInboxTaskCollection,
        NotionInboxTask,
        None,
        NotionInboxTask.DirectInfo,
        NotionInboxTask.InverseInfo]):
    """The service class for syncing inbox tasks."""

    def __init__(
            self, storage_engine: DomainStorageEngine, inbox_task_notion_manager: InboxTaskNotionManager) -> None:
        """Constructor."""
        super().__init__(
            InboxTaskCollection,
            InboxTask,
            NotionInboxTask,
            storage_engine,
            inbox_task_notion_manager)
