"""A manager of Notion-side smart lists."""
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_collection import NotionSmartListCollection
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.notion_manager import NotionBranchEntityNotFoundError, NotionLeafEntityNotFoundError, \
    ParentTrunkBranchLeafAndTagNotionManager


class NotionSmartListNotFoundError(NotionBranchEntityNotFoundError):
    """Exception raised when a Notion smart list was not found."""


class NotionSmartListTagNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion smart list tag was not found."""


class NotionSmartListItemNotFoundError(NotionLeafEntityNotFoundError):
    """Exception raised when a Notion smart list item was not found."""


class SmartListNotionManager(
        ParentTrunkBranchLeafAndTagNotionManager[
            NotionWorkspace,
            NotionSmartListCollection,
            NotionSmartList,
            NotionSmartListItem,
            NotionSmartListTag,
            None]):
    """A manager of Notion-side smart lists."""
