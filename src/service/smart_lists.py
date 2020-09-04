"""The service for dealing with smart lists."""
import logging
from typing import Final

from remote.notion.common import NotionPageLink
from remote.notion.smart_lists_manager import NotionSmartListsManager
from repository.smart_lists import SmartList, SmartListsRepository, SmartListItemsRepository, SmartListItem

LOGGER = logging.getLogger(__name__)


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

    def create_smart_list(self) -> SmartList:
        """Create a new smart list."""

        # Retrieve the current root page

        root_page = self._notion_smart_lists_manager.get_root_page()

        new_smart_list = self._smart_lists_repository.create_smart_list()
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(root_page)
        LOGGER.info("Applied remote changes")

        return new_smart_list

    def create_smart_list_item(self) -> SmartListItem:
        """Create a new list item."""

        smart_list = self._smart_lists_repository.load_smart_list()

        new_list_item = self._smart_list_items_repository.create_smart_list_item()
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list_item()
        LOGGER.info("Applied remote changes")

        return new_list_item
