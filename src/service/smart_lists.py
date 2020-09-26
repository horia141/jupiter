"""The service for dealing with smart lists."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from models.basic import EntityId, ModelValidationError, BasicValidator, SyncPrefer, SmartListKey
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.smart_lists_manager import NotionSmartListsManager
from repository.smart_lists import SmartListsRepository, SmartListItemsRepository
from service.errors import ServiceValidationError, ServiceError
from utils.storage import StructuredStorageError
from utils.time_field_action import TimeFieldAction

LOGGER = logging.getLogger(__name__)


@dataclass()
class SmartList:
    """A smart list."""
    ref_id: EntityId
    key: SmartListKey
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

    def create_smart_list(self, key: SmartListKey, name: str) -> SmartList:
        """Create a new smart list."""
        new_smart_list_row = self._smart_lists_repository.create_smart_list(key=key, name=name, archived=False)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(new_smart_list_row.ref_id, name)
        LOGGER.info("Applied remote changes")

        return SmartList(
            ref_id=new_smart_list_row.ref_id,
            key=new_smart_list_row.key,
            name=new_smart_list_row.name,
            archived=new_smart_list_row.archived)

    def archive_smart_list(self, ref_id: EntityId) -> SmartList:
        """Archive a smart list."""
        smart_list_row = self._smart_lists_repository.archive_smart_list(ref_id)

        for smart_list_item in \
                self._smart_list_items_repository.find_all_smart_list_items(
                        filter_smart_list_ref_ids=[smart_list_row.ref_id]):
            self._smart_list_items_repository.archive_smart_list_item(smart_list_item.ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartList(
            ref_id=smart_list_row.ref_id,
            key=smart_list_row.key,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

    def set_smart_list_name(self, ref_id: EntityId, name: str) -> SmartList:
        """Change the name of a smart list."""
        try:
            name = self._basic_validator.entity_name_validate_and_clean(name)
        except ModelValidationError as error:
            raise ServiceValidationError("Invalid inputs") from error

        smart_list_row = self._smart_lists_repository.load_smart_list(ref_id)
        smart_list_row.name = name
        self._smart_lists_repository.update_smart_list(smart_list_row)
        LOGGER.info("Applied local changes")

        self._notion_smart_lists_manager.upsert_smart_list(ref_id, name)
        LOGGER.info("Applied remote changes")

        return SmartList(
            ref_id=smart_list_row.ref_id,
            key=smart_list_row.key,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

    def load_smart_list_by_key(self, key: SmartListKey, allow_archived: bool = False) -> SmartList:
        """Retrieve a smart list by key."""
        smart_list_row = self._smart_lists_repository.load_smart_list_by_key(key=key, allow_archived=allow_archived)
        return SmartList(
            ref_id=smart_list_row.ref_id,
            key=smart_list_row.key,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

    def load_all_smart_lists(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> Iterable[SmartList]:
        """Retrieve all the smart list items."""
        smart_list_rows = self._smart_lists_repository.find_all_smart_lists(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_keys=filter_keys)

        return [SmartList(ref_id=slr.ref_id,
                          key=slr.key,
                          name=slr.name,
                          archived=slr.archived) for slr in smart_list_rows]

    def hard_remove_smart_list(self, ref_id: EntityId) -> SmartList:
        """Archive a smart list."""
        smart_list_row = self._smart_lists_repository.remove_smart_list(ref_id)

        for smart_list_item in \
                self._smart_list_items_repository.find_all_smart_list_items(
                        filter_smart_list_ref_ids=[smart_list_row.ref_id]):
            self._smart_list_items_repository.remove_smart_list_item(smart_list_item.ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartList(
            ref_id=smart_list_row.ref_id,
            key=smart_list_row.key,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

    def remove_smart_list_on_notion_side(self, ref_id: EntityId) -> SmartList:
        """Remove collection for a smart list Notion-side."""
        smart_list_row = self._smart_lists_repository.load_smart_list(ref_id, allow_archived=True)

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartList(
            ref_id=smart_list_row.ref_id,
            key=smart_list_row.key,
            name=smart_list_row.name,
            archived=smart_list_row.archived)

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
        self._smart_list_items_repository.update_smart_list_item(smart_list_item_row)
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
        self._smart_list_items_repository.update_smart_list_item(smart_list_item_row)
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
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListItem]:
        """Retrieve all the smart list items."""
        smart_list_item_rows = self._smart_list_items_repository.find_all_smart_list_items(
            allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
            filter_smart_list_ref_ids=filter_smart_list_ref_ids)

        return [SmartListItem(ref_id=slir.ref_id,
                              smart_list_ref_id=slir.smart_list_ref_id,
                              name=slir.name,
                              url=slir.url,
                              archived=slir.archived) for slir in smart_list_item_rows]

    def hard_remove_smart_list_item(self, ref_id: EntityId) -> SmartListItem:
        """Hard remove a list item."""
        smart_list_item_row = self._smart_list_items_repository.remove_smart_list_item(ref_id)
        LOGGER.info("Applied local changes")

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list_item(
                smart_list_item_row.smart_list_ref_id, smart_list_item_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)

    def remove_smart_list_item_on_notion_side(self, ref_id: EntityId) -> SmartListItem:
        """Remove entry for a smart list item on Notion-side."""
        smart_list_item_row = self._smart_list_items_repository.load_smart_list_item(ref_id, allow_archived=True)

        try:
            self._notion_smart_lists_manager.hard_remove_smart_list_item(smart_list_item_row.smart_list_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

        return SmartListItem(
            ref_id=smart_list_item_row.ref_id,
            smart_list_ref_id=smart_list_item_row.smart_list_ref_id,
            name=smart_list_item_row.name,
            url=smart_list_item_row.url,
            archived=smart_list_item_row.archived)

    def sync_smart_list_and_smart_list_items(
            self, smart_list_ref_id: EntityId, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[SmartListItem]:
        """Synchronise a smart list and its items between Notion and local storage."""
        # Synchronize the smart list.
        smart_list_row = self._smart_lists_repository.load_smart_list(smart_list_ref_id)
        smart_list_notion_collection = self._notion_smart_lists_manager.load_smart_list(smart_list_ref_id)

        if sync_prefer == SyncPrefer.LOCAL:
            smart_list_notion_collection.name = smart_list_row.name
            self._notion_smart_lists_manager.save_smart_list(smart_list_notion_collection)
            LOGGER.info("Applied changes to Notion")
        elif sync_prefer == SyncPrefer.NOTION:
            smart_list_row.name = smart_list_notion_collection.name
            self._smart_lists_repository.update_smart_list(smart_list_row)
            LOGGER.info("Applied local change")
        else:
            raise Exception(f"Invalid preference {sync_prefer}")

        # Now synchronize the list items here.
        filter_smart_list_item_ref_ids_set = frozenset(filter_smart_list_item_ref_ids) \
            if filter_smart_list_item_ref_ids else None

        all_smart_list_items_rows = self._smart_list_items_repository.find_all_smart_list_items(
            allow_archived=True, filter_smart_list_ref_ids=filter_smart_list_item_ref_ids)
        all_smart_list_items_rows_set = {sli.ref_id: sli for sli in all_smart_list_items_rows}

        if not drop_all_notion_side:
            all_smart_list_items_notion_rows = \
                self._notion_smart_lists_manager.load_all_smart_list_items(smart_list_ref_id)
            all_smart_list_items_notion_ids = \
                set(self._notion_smart_lists_manager.load_all_saved_smart_list_items_notion_ids(smart_list_ref_id))
        else:
            self._notion_smart_lists_manager.drop_all_smart_list_items(smart_list_ref_id)
            all_smart_list_items_notion_rows = []
            all_smart_list_items_notion_ids = set()
        smart_list_items_notion_rows_set = {}

        # Explore Notion and apply to local
        for smart_list_item_notion_row in all_smart_list_items_notion_rows:
            if filter_smart_list_item_ref_ids_set is not None and \
                    smart_list_item_notion_row.ref_id not in filter_smart_list_item_ref_ids_set:
                LOGGER.info(f"Skipping '{smart_list_item_notion_row.name}' (id={smart_list_item_notion_row.notion_id})")
                continue

            LOGGER.info(f"Syncing '{smart_list_item_notion_row.name}' (id={smart_list_item_notion_row.notion_id})")

            if smart_list_item_notion_row.ref_id is None or smart_list_item_notion_row.ref_id == "":
                # If the smart list item doesn't exist locally, we create it.
                try:
                    smart_list_item_name = \
                        self._basic_validator.entity_name_validate_and_clean(smart_list_item_notion_row.name)
                    smart_list_item_url = \
                        self._basic_validator.url_validate_and_clean(smart_list_item_notion_row.url) \
                            if smart_list_item_notion_row.url else None
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                new_smart_list_item_row = self._smart_list_items_repository.create_smart_list_item(
                    smart_list_ref_id=smart_list_ref_id,
                    name=smart_list_item_name,
                    url=smart_list_item_url,
                    archived=smart_list_item_notion_row.archived)
                LOGGER.info(f"Found new smart list item from Notion '{new_smart_list_item_row.name}'")

                self._notion_smart_lists_manager.link_local_and_notion_entries_for_smart_list(
                    smart_list_ref_id, new_smart_list_item_row.ref_id, smart_list_item_notion_row.notion_id)
                LOGGER.info(f"Linked the new smart list item with local entries")

                smart_list_item_notion_row.ref_id = new_smart_list_item_row.ref_id
                self._notion_smart_lists_manager.save_smart_list_item(
                    smart_list_ref_id, new_smart_list_item_row.ref_id, smart_list_item_notion_row)
                LOGGER.info(f"Applied changes on Notion side too")

                smart_list_items_notion_rows_set[EntityId(smart_list_item_notion_row.ref_id)] = \
                    smart_list_item_notion_row
            elif smart_list_item_notion_row.ref_id in all_smart_list_items_rows_set and \
                    smart_list_item_notion_row.notion_id in all_smart_list_items_notion_ids:
                smart_list_item_row = all_smart_list_items_rows_set[EntityId(smart_list_item_notion_row.ref_id)]
                smart_list_items_notion_rows_set[EntityId(smart_list_item_notion_row.ref_id)] = \
                    smart_list_item_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            smart_list_item_notion_row.last_edited_time <= smart_list_item_row.last_modified_time:
                        LOGGER.info(f"Skipping '{smart_list_item_notion_row.name}' because it was not modified")
                        continue

                    try:
                        smart_list_item_name = \
                            self._basic_validator.entity_name_validate_and_clean(smart_list_item_notion_row.name)
                        smart_list_item_url = \
                            self._basic_validator.url_validate_and_clean(smart_list_item_notion_row.url) \
                                if smart_list_item_notion_row.url else None
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    archived_time_action = \
                        TimeFieldAction.SET if not smart_list_item_row.archived \
                                               and smart_list_item_notion_row.archived else \
                        TimeFieldAction.CLEAR if smart_list_item_row.archived \
                                                 and not smart_list_item_notion_row.archived else \
                        TimeFieldAction.DO_NOTHING
                    smart_list_item_row.archived = smart_list_item_notion_row.archived
                    smart_list_item_row.name = smart_list_item_name
                    smart_list_item_row.url = smart_list_item_url
                    self._smart_list_items_repository.update_smart_list_item(smart_list_item_row, archived_time_action)
                    LOGGER.info(f"Changed smart list item '{smart_list_item_row.name}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            smart_list_item_row.last_modified_time <= smart_list_item_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping '{smart_list_item_notion_row.name}' because it was not modified")
                        continue

                    smart_list_item_notion_row.archived = smart_list_item_row.archived
                    smart_list_item_notion_row.name = smart_list_item_row.name
                    smart_list_item_notion_row.url = smart_list_item_row.url
                    self._notion_smart_lists_manager.save_smart_list_item(
                        smart_list_ref_id, smart_list_item_row.ref_id, smart_list_item_notion_row)
                    LOGGER.info(f"Changed small list item with '{smart_list_item_notion_row.name}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random smart list item added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_smart_lists_manager.hard_remove_smart_list_item(
                    smart_list_ref_id, EntityId(smart_list_item_notion_row.ref_id))
                LOGGER.info(f"Removed smart list item with id={smart_list_item_notion_row.ref_id} from Notion")

        for smart_list_item_row in all_smart_list_items_rows:
            if smart_list_item_row.ref_id in smart_list_items_notion_rows_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if smart_list_item_row.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            self._notion_smart_lists_manager.upsert_smart_list_item(
                smart_list_ref_id=smart_list_ref_id,
                ref_id=smart_list_item_row.ref_id,
                name=smart_list_item_row.name,
                url=smart_list_item_row.url,
                archived=smart_list_item_row.archived)
            LOGGER.info(f"Created new smart list item on Notion side '{smart_list_item_row.name}'")

        return [SmartListItem(
            ref_id=slir.ref_id,
            smart_list_ref_id=slir.smart_list_ref_id,
            name=slir.name,
            url=slir.url,
            archived=slir.archived) for slir in all_smart_list_items_rows_set.values()]
