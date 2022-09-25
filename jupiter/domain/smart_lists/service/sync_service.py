"""Shared service for syncing smart lists."""
from jupiter.domain.notion_sync_service import TrunkBranchLeafAndTagNotionSyncService
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_collection import (
    NotionSmartListCollection,
)
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace


class SmartListSyncServiceNew(
    TrunkBranchLeafAndTagNotionSyncService[
        SmartListCollection,
        SmartList,
        SmartListItem,
        SmartListTag,
        NotionWorkspace,
        NotionSmartListCollection,
        NotionSmartList,
        NotionSmartListItem,
        NotionSmartListTag,
    ]
):
    """The service class for syncing smart lists."""

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(
            SmartListCollection,
            SmartList,
            "smart list",
            SmartListItem,
            "smart list item",
            SmartListTag,
            "smart list tag",
            NotionSmartList,
            NotionSmartListItem,
            NotionSmartListTag,
            storage_engine,
            smart_list_notion_manager,
        )
