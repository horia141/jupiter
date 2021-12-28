"""A manager of Notion-side smart lists."""
import abc
from typing import Iterable, Optional

from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.workspaces.notion_workspace import NotionWorkspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import NotionId


class NotionSmartListNotFoundError(Exception):
    """Exception raised when a Notion smart list was not found."""


class NotionSmartListTagNotFoundError(Exception):
    """Exception raised when a Notion smart list tag was not found."""


class NotionSmartListItemNotFoundError(Exception):
    """Exception raised when a Notion smart list item was not found."""


class SmartListNotionManager(abc.ABC):
    """A manager of Notion-side smart lists."""

    @abc.abstractmethod
    def upsert_root_page(self, notion_workspace: NotionWorkspace) -> None:
        """Upsert the root page for the smart lists section."""

    @abc.abstractmethod
    def upsert_smart_list(self, smart_list: NotionSmartList) -> NotionSmartList:
        """Upsert a smart list on Notion-side."""

    @abc.abstractmethod
    def save_smart_list(self, smart_list: NotionSmartList) -> NotionSmartList:
        """Save a smart list on Notion-side."""

    @abc.abstractmethod
    def load_smart_list(self, ref_id: EntityId) -> NotionSmartList:
        """Retrieve a smart list from Notion-side."""

    @abc.abstractmethod
    def remove_smart_list(self, ref_id: EntityId) -> None:
        """Remove a smart list on Notion-side."""

    @abc.abstractmethod
    def upsert_smart_list_tag(
            self, smart_list_ref_id: EntityId, smart_list_tag: NotionSmartListTag) -> NotionSmartListTag:
        """Upsert a smart list tag on Notion-side."""

    @abc.abstractmethod
    def save_smart_list_tag(
            self, smart_list_ref_id: EntityId, smart_list_tag: NotionSmartListTag) -> NotionSmartListTag:
        """Update the Notion-side smart list tag with new data."""

    @abc.abstractmethod
    def load_smart_list_tag(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> NotionSmartListTag:
        """Retrieve all the Notion-side smart list tags."""

    @abc.abstractmethod
    def load_all_smart_list_tags(self, smart_list_ref_id: EntityId) -> Iterable[NotionSmartListTag]:
        """Retrieve all the Notion-side smart list tags."""

    @abc.abstractmethod
    def remove_smart_list_tag(self, smart_list_ref_id: EntityId, ref_id: Optional[EntityId]) -> None:
        """Remove a smart list tag on Notion-side."""

    @abc.abstractmethod
    def drop_all_smart_list_tags(self, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list tags Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_tag_for_smart_list(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local tag with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_smart_list_tags_notion_ids(self, smart_list_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the Notion ids for the smart list tags."""

    @abc.abstractmethod
    def upsert_smart_list_item(
            self, smart_list_ref_id: EntityId, smart_list_item: NotionSmartListItem) -> NotionSmartListItem:
        """Upsert a smart list item on Notion-side."""

    @abc.abstractmethod
    def save_smart_list_item(
            self, smart_list_ref_id: EntityId, smart_list_item: NotionSmartListItem) -> NotionSmartListItem:
        """Update the Notion-side smart list with new data."""

    @abc.abstractmethod
    def load_smart_list_item(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> NotionSmartListItem:
        """Retrieve a particular smart list item."""

    @abc.abstractmethod
    def load_all_smart_list_items(self, smart_list_ref_id: EntityId) -> Iterable[NotionSmartListItem]:
        """Retrieve all the Notion-side smart list items."""

    @abc.abstractmethod
    def remove_smart_list_item(self, smart_list_ref_id: EntityId, ref_id: EntityId) -> None:
        """Remove a smart list item on Notion-side."""

    @abc.abstractmethod
    def drop_all_smart_list_items(self, smart_list_ref_id: EntityId) -> None:
        """Remove all smart list items Notion-side."""

    @abc.abstractmethod
    def link_local_and_notion_entries_for_smart_list(
            self, smart_list_ref_id: EntityId, ref_id: EntityId, notion_id: NotionId) -> None:
        """Link a local entity with the Notion one, useful in syncing processes."""

    @abc.abstractmethod
    def load_all_saved_smart_list_items_notion_ids(self, smart_list_ref_id: EntityId) -> Iterable[NotionId]:
        """Retrieve all the saved Notion-ids for these smart lists items."""

    @abc.abstractmethod
    def load_all_saved_smart_list_items_ref_ids(self, smart_list_ref_id: EntityId) -> Iterable[EntityId]:
        """Retrieve all the saved ref ids for the smart list items."""
