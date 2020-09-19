"""The service for dealing with smart lists."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from models.basic import EntityId, ModelValidationError, BasicValidator
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.smart_lists_manager import NotionSmartListsManager
from repository.smart_lists import SmartListsRepository, SmartListItemsRepository
from service.errors import ServiceValidationError

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

    _basic_validator: Final[BasicValidator]
    _smart_lists_repository: Final[SmartListsRepository]
    _smart_list_items_repository: Final[SmartListItemsRepository]
    _notion_smart_lists_manager: Final[NotionSmartListsManager]

    def __init__(
            self, basic_validator: BasicValidator, smart_lists_repository: SmartListsRepository,
            smart_list_items_repository: SmartListItemsRepository,
            notion_smart_lists_manager: NotionSmartListsManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._smart_lists_repository = smart_lists_repository
        self._smart_list_items_repository = smart_list_items_repository
        self._notion_smart_lists_manager = notion_smart_lists_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all lists will be linked to."""
        self._notion_smart_lists_manager.upsert_root_page(parent_page)

    def create_smart_list(self, name: str) -> SmartList:
        """Create a new smart list."""
        new_smart_list_row = self._smart_lists_repository.create_smart_list(name, archived=False)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(new_smart_list_row.ref_id, name)
        LOGGER.info("Applied remote changes")

        return SmartList(
            ref_id=new_smart_list_row.ref_id,
            name=new_smart_list_row.name,
            archived=new_smart_list_row.archived)

    def archive_smart_list(self, ref_id: EntityId) -> SmartList:
        """Archive a smart list."""
        smart_list = self._smart_lists_repository.archive_smart_list(ref_id)

        for smart_list_item in \
                self._smart_list_items_repository.load_all_smart_list_items(
                    filter_smart_list_ref_ids=[smart_list.ref_id]):
            self._smart_list_items_repository.archive_smart_list_item(smart_list_item.ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartList(
            ref_id=smart_list.ref_id,
            name=smart_list.name,
            archived=smart_list.archived)

    def set_smart_list_name(self, ref_id: EntityId, name: str) -> SmartList:
        """Change the name of a smart list."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        smart_list_row = self._smart_lists_repository.load_smart_list(ref_id)
        smart_list_row.name = name
        self._smart_lists_repository.save_smart_list(smart_list_row)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(ref_id, name)
        LOGGER.info("Applied remote changes")

        return SmartList(
            ref_id=smart_list_row.ref_id,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

    def load_all_smart_lists(
        self, filter_archived: bool = True,
        filter_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartList]:
        """Retrieve all the smart list items."""
        smart_list_rows = self._smart_lists_repository.load_all_smart_lists(
            filter_archived=filter_archived, filter_ref_ids=filter_ref_ids)

        return [SmartList(ref_id=slr.ref_id,
                          name=slr.name,
                          archived=slr.archived) for slr in smart_list_rows]

    def hard_remove_smart_list(self, ref_id: EntityId) -> SmartList:
        """Archive a smart list."""
        smart_list = self._smart_lists_repository.hard_remove_smart_list(ref_id)

        for smart_list_item in \
                self._smart_list_items_repository.load_all_smart_list_items(
                    filter_smart_list_ref_ids=[smart_list.ref_id]):
            self._smart_list_items_repository.hard_remove_smart_list_item(smart_list_item.ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartList(
            ref_id=smart_list.ref_id,
            name=smart_list.name,
            archived=smart_list.archived)

    def create_smart_list_item(self, smart_list_ref_id: EntityId, name: str, url: Optional[str]) -> SmartListItem:
        """Create a new list item."""
        smart_list_row = self._smart_lists_repository.load_smart_list(ref_id=smart_list_ref_id)

        new_smart_list_item_row = self._smart_list_items_repository.create_smart_list_item(
            smart_list_ref_id=smart_list_row.ref_id,
            name=name,
            url=url,
            archived=False)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list_item(
            smart_list_ref_id=smart_list_row.ref_id,
            ref_id=new_smart_list_item_row.ref_id,
            name=new_smart_list_item_row.name,
            url=new_smart_list_item_row.url,
            archived=new_smart_list_item_row.archived)

        LOGGER.info("Applied remote changes")

        return SmartListItem(
            ref_id=new_smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_ref_id,
            name=new_smart_list_item_row.name,
            url=new_smart_list_item_row.url,
            archived=new_smart_list_item_row.archived)

    def archive_smart_list_item(self, ref_id: EntityId) -> SmartListItem:
        """Archive a list item."""
        smart_list_item_row = self._smart_list_items_repository.archive_smart_list_item(ref_id)
        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.archive_smart_list_item(
                smart_list_item_row.smart_list_ref_id, smart_list_item_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because recurring task was not found")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)

    def set_smart_list_item_name(self, ref_id: EntityId, name: str) -> SmartListItem:
        """Change the name of a smart list item."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        smart_list_item_row = self._smart_list_items_repository.load_smart_list_item(ref_id)
        smart_list_item_row.name = name
        self._smart_list_items_repository.save_smart_list_item(smart_list_item_row)
        LOGGER.info("Applied local changes")

        smart_list_item_notion_row = self._notion_smart_lists_manager.load_smart_list_item(
            smart_list_item_row.smart_list_ref_id, ref_id)
        smart_list_item_notion_row.name = name
        self._notion_smart_lists_manager.save_smart_list_item(
            smart_list_item_row.smart_list_ref_id, ref_id, smart_list_item_notion_row)
        LOGGER.info("Applied Notion changes")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)

    def set_smart_list_item_url(self, ref_id: EntityId, url: Optional[str]) -> SmartListItem:
        """Change the name of a smart list item."""
        try:
            url = self._basic_validator.url_validate_and_clean(url) if url else None
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        smart_list_item_row = self._smart_list_items_repository.load_smart_list_item(ref_id)
        smart_list_item_row.url = url
        self._smart_list_items_repository.save_smart_list_item(smart_list_item_row)
        LOGGER.info("Applied local changes")

        smart_list_item_notion_row = self._notion_smart_lists_manager.load_smart_list_item(
            smart_list_item_row.smart_list_ref_id, ref_id)
        smart_list_item_notion_row.url = url
        self._notion_smart_lists_manager.save_smart_list_item(
            smart_list_item_row.smart_list_ref_id, ref_id, smart_list_item_notion_row)
        LOGGER.info("Applied Notion changes")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)

    def load_all_smart_list_items(
            self, filter_archived: bool = True, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListItem]:
        """Retrieve all the smart list items."""
        smart_list_item_rows = self._smart_list_items_repository.load_all_smart_list_items(
            filter_archived=filter_archived, filter_ref_ids=filter_ref_ids,
            filter_smart_list_ref_ids=filter_smart_list_ref_ids)

        return [SmartListItem(ref_id=slir.ref_id,
                              smart_list_ref_id=slir.smart_list_ref_id,
                              name=slir.name,
                              url=slir.url,
                              archived=slir.archived) for slir in smart_list_item_rows]

    def hard_remove_smart_list_item(self, ref_id: EntityId) -> SmartListItem:
        """Hard remove a list item."""
        smart_list_item_row = self._smart_list_items_repository.hard_remove_smart_list_item(ref_id)
        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list_item(
                smart_list_item_row.smart_list_ref_id, smart_list_item_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)
