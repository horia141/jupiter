"""The service for dealing with smart lists."""
import logging
from dataclasses import dataclass
from typing import Final, Optional

from models.basic import EntityId
from remote.notion.common import NotionPageLink
from remote.notion.smart_lists_manager import NotionSmartListsManager
from repository.smart_lists import SmartListsRepository, SmartListItemsRepository

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartList:
    """A smart list."""
    ref_id: EntityId
    name: str
    archived: bool


@dataclass()
class SmartListItem:
    """A smart list item."""
    ref_id: EntityId
    smart_list_ref_id: EntityId
    name: str
    url: Optional[str]
    archived: bool


class SmartListsService:
    """The service class for dealing with smart lists."""

    _smart_lists_repository: Final[SmartListsRepository]
    _smart_list_items_repository: Final[SmartListItemsRepository]
    _notion_smart_lists_manager: Final[NotionSmartListsManager]

    def __init__(
            self, smart_lists_repository: SmartListsRepository, smart_list_items_repository: SmartListItemsRepository,
            notion_smart_lists_manager: NotionSmartListsManager) -> None:
        """Constructor."""
        self._smart_lists_repository = smart_lists_repository
        self._smart_list_items_repository = smart_list_items_repository
        self._notion_smart_lists_manager = notion_smart_lists_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all lists will be linked to."""
        self._notion_smart_lists_manager.upsert_root_page(parent_page)

    def create_smart_list(self, name: str) -> SmartList:
        """Create a new smart list."""
        new_smart_list_row = self._smart_lists_repository.create_smart_list(name)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(new_smart_list_row.ref_id, name)
        LOGGER.info("Applied remote changes")

        return SmartList(
            ref_id=new_smart_list_row.ref_id,
            name=new_smart_list_row.name,
            archived=new_smart_list_row.archived)

    def create_smart_list_item(self, name: str, url: Optional[str]) -> SmartListItem:
        """Create a new list item."""
        smart_list_row = self._smart_lists_repository.load_smart_list()

        new_smart_list_item_row = self._smart_list_items_repository.create_smart_list_item()
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list_item(
            smart_list_row.ref_id, new_smart_list_item_row.ref_id, name, url)
        LOGGER.info("Applied remote changes")

        return SmartListItem(
            ref_id=new_smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_row.ref_id,
            name=new_smart_list_item_row.name,
            url=new_smart_list_item_row.url,
            archived=new_smart_list_item_row.archived)
