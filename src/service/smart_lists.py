"""The service for dealing with smart lists."""
import logging
from typing import Final, Optional, Iterable

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.smart_list import SmartList
from domain.smart_lists.smart_list_item import SmartListItem
from domain.smart_lists.smart_list_tag import SmartListTag
from models.basic import BasicValidator, SyncPrefer, SmartListKey, Tag
from models.framework import EntityId
from models.errors import ModelValidationError
from remote.notion.common import NotionPageLink, CollectionEntityNotFound
from remote.notion.smart_lists_manager import NotionSmartListsManager
from service.errors import ServiceValidationError, ServiceError
from utils.storage import StructuredStorageError
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListsService:
    """The service class for dealing with smart lists."""

    _basic_validator: Final[BasicValidator]
    _time_provider: Final[TimeProvider]
    _smart_list_engine: Final[SmartListEngine]
    _notion_manager: Final[NotionSmartListsManager]

    def __init__(
            self, basic_validator: BasicValidator, time_provider: TimeProvider,
            smart_list_engine: SmartListEngine, notion_manager: NotionSmartListsManager) -> None:
        """Constructor."""
        self._basic_validator = basic_validator
        self._time_provider = time_provider
        self._smart_list_engine = smart_list_engine
        self._notion_manager = notion_manager

    def upsert_root_notion_structure(self, parent_page: NotionPageLink) -> None:
        """Create the root page where all lists will be linked to."""
        self._notion_manager.upsert_root_page(parent_page)

    def upsert_smart_list_structure(self, ref_id: EntityId) -> None:
        """Upsert the structure around a smart list."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list_row = uow.smart_list_repository.get_by_id(ref_id)
        self._notion_manager.upsert_smart_list_collection(ref_id, smart_list_row.name)

    def load_all_smart_lists(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[SmartListKey]] = None) -> Iterable[SmartList]:
        """Retrieve all the smart lists."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            return uow.smart_list_repository.find_all(
                allow_archived=allow_archived, filter_ref_ids=filter_ref_ids, filter_keys=filter_keys)

    def hard_remove_smart_list(self, ref_id: EntityId) -> None:
        """Archive a smart list."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            for smart_list_item in \
                    uow.smart_list_item_repository.find_all(
                            allow_archived=True, filter_smart_list_ref_ids=[ref_id]):
                uow.smart_list_item_repository.remove(smart_list_item.ref_id)

            for smart_list_tag in \
                    uow.smart_list_tag_repository.find_all(
                            allow_archived=True, filter_smart_list_ref_ids=[ref_id]):
                uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)

            uow.smart_list_repository.remove(ref_id)

        LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_smart_list_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping removal on Notion side because smart list was not found")

    def remove_smart_list_on_notion_side(self, ref_id: EntityId) -> None:
        """Remove collection for a smart list Notion-side."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            uow.smart_list_repository.get_by_id(ref_id, allow_archived=True)

        try:
            self._notion_manager.hard_remove_smart_list_collection(ref_id)
            LOGGER.info("Applied Notion changes")
        except CollectionEntityNotFound:
            LOGGER.info("Skipping removal on Notion side because smart list was not found")

    def load_all_smart_list_tags(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_smart_list_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[SmartListTag]:
        """Retrieve all the smart list tags."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            return uow.smart_list_tag_repository.find_all(
                allow_archived=allow_archived, filter_ref_ids=filter_ref_ids,
                filter_smart_list_ref_ids=filter_smart_list_ref_ids)

    def hard_remove_smart_list_tag(self, ref_id: EntityId) -> None:
        """Hard remove a list tag."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list_tag = uow.smart_list_tag_repository.load_by_id(ref_id)
            smart_list_items = uow.smart_list_item_repository.find_all(
                allow_archived=True,
                filter_smart_list_ref_ids=[smart_list_tag.smart_list_ref_id],
                filter_tag_ref_ids=[ref_id])

            for smart_list_item in smart_list_items:
                smart_list_item.change_tags(
                    [t for t in smart_list_item.tags if t != ref_id], self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

            uow.smart_list_tag_repository.remove(ref_id)
            LOGGER.info("Applied local changes")

        self._notion_manager.hard_remove_smart_list_tag(smart_list_tag.smart_list_ref_id, ref_id)
        LOGGER.info("Applied remote changes")

    def load_all_smart_list_items(self, allow_archived: bool = False) -> Iterable[SmartListItem]:
        """Retrieve all the smart list items."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            return uow.smart_list_item_repository.find_all(
                allow_archived=allow_archived)

    def load_all_smart_list_items_not_notion_gced(self, smart_list_ref_id: EntityId) -> Iterable[SmartListItem]:
        """Retrieve all smart list items which haven't been gced on Notion side."""
        allowed_ref_ids = set(self._notion_manager.load_all_saved_smart_list_items_ref_ids(smart_list_ref_id))
        with self._smart_list_engine.get_unit_of_work() as uow:
            return uow.smart_list_item_repository.find_all(
                allow_archived=True, filter_ref_ids=allowed_ref_ids, filter_smart_list_ref_ids=[smart_list_ref_id])

    def hard_remove_smart_list_item(self, ref_id: EntityId) -> None:
        """Hard remove a list item."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list_item_row = uow.smart_list_item_repository.remove(ref_id)
            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.hard_remove_smart_list_item(
                smart_list_item_row.smart_list_ref_id, smart_list_item_row.ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping har removal on Notion side because recurring task was not found")

    def remove_smart_list_item_on_notion_side(self, ref_id: EntityId) -> None:
        """Remove entry for a smart list item on Notion-side."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list_item_row = uow.smart_list_item_repository.load_by_id(ref_id, allow_archived=True)

        try:
            self._notion_manager.hard_remove_smart_list_item(smart_list_item_row.smart_list_ref_id, ref_id)
            LOGGER.info("Applied Notion changes")
        except StructuredStorageError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")

    def sync_smart_list_and_smart_list_items(
            self, smart_list_ref_id: EntityId, drop_all_notion_side: bool, sync_even_if_not_modified: bool,
            filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[SmartListItem]:
        """Synchronise a smart list and its items between Notion and local storage."""
        # Synchronize the smart list.
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.get_by_id(smart_list_ref_id)

        try:
            smart_list_notion_collection = self._notion_manager.load_smart_list_collection(smart_list_ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                smart_list_notion_collection.name = smart_list.name
                self._notion_manager.save_smart_list_collection(smart_list_notion_collection)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                with self._smart_list_engine.get_unit_of_work() as uow:
                    smart_list.change_name(
                        self._basic_validator.entity_name_validate_and_clean(smart_list_notion_collection.name),
                        self._time_provider.get_current_time())
                    uow.smart_list_repository.save(smart_list)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except StructuredStorageError:
            LOGGER.info("Trying to recreate the smart list")
            self._notion_manager.upsert_smart_list_collection(smart_list_ref_id, smart_list.name)

        # Synchronise the tags here.
        with self._smart_list_engine.get_unit_of_work() as uow:
            all_smart_list_tags = list(uow.smart_list_tag_repository.find_all(
                allow_archived=True, filter_smart_list_ref_ids=[smart_list_ref_id]))
        all_smart_list_tags_set = {slt.ref_id: slt for slt in all_smart_list_tags}
        all_smart_list_tags_by_name = {slt.name: slt for slt in all_smart_list_tags}

        if not drop_all_notion_side:
            all_smart_list_tags_notion_rows = \
                self._notion_manager.load_all_smart_list_tags(smart_list_ref_id)
            all_smart_list_tags_notion_ids = \
                set(self._notion_manager.load_all_saved_smart_list_tags_notion_ids(smart_list_ref_id))
        else:
            self._notion_manager.drop_all_smart_list_tags(smart_list_ref_id)
            all_smart_list_tags_notion_rows = []
            all_smart_list_tags_notion_ids = set()
        smart_list_tags_notion_rows_set = {}

        for smart_list_tag_notion_row in all_smart_list_tags_notion_rows:
            notion_smart_list_tag_ref_id = EntityId.from_raw(smart_list_tag_notion_row.ref_id)\
                if smart_list_tag_notion_row.ref_id else None
            LOGGER.info(f"Syncing tag '{smart_list_tag_notion_row.name}' (id={smart_list_tag_notion_row.notion_id})")

            if notion_smart_list_tag_ref_id is None or smart_list_tag_notion_row.ref_id == "":
                # If the smart list tag doesn't exist locally, we create it.
                try:
                    smart_list_tag_name = self._basic_validator.tag_validate_and_clean(smart_list_tag_notion_row.name)
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                with self._smart_list_engine.get_unit_of_work() as uow:
                    new_smart_list_tag = SmartListTag.new_smart_list_tag(
                        smart_list_ref_id, smart_list_tag_name, self._time_provider.get_current_time())
                    new_smart_list_tag = uow.smart_list_tag_repository.create(new_smart_list_tag)
                LOGGER.info(f"Found new smart list tag from Notion '{new_smart_list_tag.name}'")

                self._notion_manager.link_local_and_notion_tag_for_smart_list(
                    smart_list_ref_id, new_smart_list_tag.ref_id, smart_list_tag_notion_row.notion_id)
                LOGGER.info(f"Linked the new smart list tag with local entries")

                smart_list_tag_notion_row.ref_id = str(new_smart_list_tag.ref_id)
                self._notion_manager.save_smart_list_tag(
                    smart_list_ref_id, new_smart_list_tag.ref_id, smart_list_tag_notion_row)
                LOGGER.info(f"Applied changes on Notion side too")

                smart_list_tags_notion_rows_set[new_smart_list_tag.ref_id] = smart_list_tag_notion_row
                all_smart_list_tags.append(new_smart_list_tag)
                all_smart_list_tags_set[new_smart_list_tag.ref_id] = new_smart_list_tag
                all_smart_list_tags_by_name[new_smart_list_tag.name] = new_smart_list_tag
            elif notion_smart_list_tag_ref_id in all_smart_list_tags_set and \
                    smart_list_tag_notion_row.notion_id in all_smart_list_tags_notion_ids:
                smart_list_tag = all_smart_list_tags_set[notion_smart_list_tag_ref_id]
                smart_list_tags_notion_rows_set[notion_smart_list_tag_ref_id] = smart_list_tag_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    try:
                        smart_list_tag_name = self._basic_validator.tag_validate_and_clean(
                            smart_list_tag_notion_row.name)
                    except ModelValidationError as error:
                        raise ServiceValidationError("Invalid inputs") from error

                    with self._smart_list_engine.get_unit_of_work() as uow:
                        smart_list_tag.change_name(smart_list_tag_name, self._time_provider.get_current_time())
                        uow.smart_list_tag_repository.save(smart_list_tag)
                    LOGGER.info(f"Changed smart list tag '{smart_list_tag.name}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    smart_list_tag_notion_row.name = smart_list_tag.name
                    self._notion_manager.save_smart_list_tag(
                        smart_list_ref_id, smart_list_tag.ref_id, smart_list_tag_notion_row)
                    LOGGER.info(f"Changed smart list tag '{smart_list_tag_notion_row.name}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random smart list tag added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_smart_list_tag(
                    smart_list_ref_id, notion_smart_list_tag_ref_id)
                LOGGER.info(f"Removed smart list item with id={smart_list_tag_notion_row.ref_id} from Notion")

        for smart_list_tag in all_smart_list_tags:
            if smart_list_tag.ref_id in smart_list_tags_notion_rows_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if smart_list_tag.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            self._notion_manager.upsert_smart_list_tag(smart_list_tag)
            LOGGER.info(f"Created new smart list tag on Notion side '{smart_list_tag.name}'")

        # Now synchronize the list items here.
        filter_smart_list_item_ref_ids_set = frozenset(filter_smart_list_item_ref_ids) \
            if filter_smart_list_item_ref_ids else None

        with self._smart_list_engine.get_unit_of_work() as uow:
            all_smart_list_items_rows = uow.smart_list_item_repository.find_all(
                allow_archived=True, filter_smart_list_ref_ids=[smart_list_ref_id],
                filter_ref_ids=filter_smart_list_item_ref_ids)
        all_smart_list_items_set = {sli.ref_id: sli for sli in all_smart_list_items_rows}

        if not drop_all_notion_side:
            all_smart_list_items_notion_rows = \
                self._notion_manager.load_all_smart_list_items(smart_list_ref_id)
            all_smart_list_items_notion_ids = \
                set(self._notion_manager.load_all_saved_smart_list_items_notion_ids(smart_list_ref_id))
        else:
            self._notion_manager.drop_all_smart_list_items(smart_list_ref_id)
            all_smart_list_items_notion_rows = []
            all_smart_list_items_notion_ids = set()
        smart_list_items_notion_rows_set = {}

        # Explore Notion and apply to local
        for smart_list_item_notion_row in all_smart_list_items_notion_rows:
            notion_smart_list_item_ref_id = EntityId.from_raw(smart_list_item_notion_row.ref_id) \
                if smart_list_item_notion_row.ref_id else None
            if filter_smart_list_item_ref_ids_set is not None and \
                    notion_smart_list_item_ref_id not in filter_smart_list_item_ref_ids_set:
                LOGGER.info(f"Skipping '{smart_list_item_notion_row.name}' (id={smart_list_item_notion_row.notion_id})")
                continue

            LOGGER.info(f"Syncing '{smart_list_item_notion_row.name}' (id={smart_list_item_notion_row.notion_id})")

            if notion_smart_list_item_ref_id is None or smart_list_item_notion_row.ref_id == "":
                # If the smart list item doesn't exist locally, we create it.
                try:
                    smart_list_item_name = \
                        self._basic_validator.entity_name_validate_and_clean(smart_list_item_notion_row.name)
                    smart_list_item_url = \
                        self._basic_validator.url_validate_and_clean(smart_list_item_notion_row.url) \
                            if smart_list_item_notion_row.url else None
                except ModelValidationError as error:
                    raise ServiceValidationError("Invalid inputs") from error

                with self._smart_list_engine.get_unit_of_work() as uow:
                    new_smart_list_item = SmartListItem.new_smart_list_item(
                        archived=smart_list_item_notion_row.archived,
                        smart_list_ref_id=smart_list_ref_id,
                        name=smart_list_item_name,
                        is_done=smart_list_item_notion_row.is_done,
                        tags_ref_id=[
                            all_smart_list_tags_by_name[Tag(t)].ref_id for t in smart_list_item_notion_row.tags
                            if Tag(t) in all_smart_list_tags_by_name],
                        url=smart_list_item_url,
                        created_time=self._time_provider.get_current_time())
                    new_smart_list_item = uow.smart_list_item_repository.create(new_smart_list_item)
                LOGGER.info(f"Found new smart list item from Notion '{new_smart_list_item.name}'")

                self._notion_manager.link_local_and_notion_entries_for_smart_list(
                    smart_list_ref_id, new_smart_list_item.ref_id, smart_list_item_notion_row.notion_id)
                LOGGER.info(f"Linked the new smart list item with local entries")

                smart_list_item_notion_row.ref_id = str(new_smart_list_item.ref_id)
                self._notion_manager.save_smart_list_item(
                    smart_list_ref_id, new_smart_list_item.ref_id, smart_list_item_notion_row)
                LOGGER.info(f"Applied changes on Notion side too")

                smart_list_items_notion_rows_set[new_smart_list_item.ref_id] = \
                    smart_list_item_notion_row
            elif notion_smart_list_item_ref_id in all_smart_list_items_set and \
                    smart_list_item_notion_row.notion_id in all_smart_list_items_notion_ids:
                smart_list_item = all_smart_list_items_set[notion_smart_list_item_ref_id]
                smart_list_items_notion_rows_set[notion_smart_list_item_ref_id] = \
                    smart_list_item_notion_row

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            smart_list_item_notion_row.last_edited_time <= smart_list_item.last_modified_time:
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

                    smart_list_item.change_name(smart_list_item_name, self._time_provider.get_current_time())
                    smart_list_item.change_is_done(
                        smart_list_item_notion_row.is_done, self._time_provider.get_current_time())
                    smart_list_item.change_tags(
                        [all_smart_list_tags_by_name[Tag(t)].ref_id for t in smart_list_item_notion_row.tags],
                        self._time_provider.get_current_time())
                    smart_list_item.change_url(smart_list_item_url, self._time_provider.get_current_time())
                    smart_list_item.change_archived(
                        smart_list_item_notion_row.archived, self._time_provider.get_current_time())
                    with self._smart_list_engine.get_unit_of_work() as uow:
                        uow.smart_list_item_repository.save(smart_list_item)
                    LOGGER.info(f"Changed smart list item '{smart_list_item.name}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            smart_list_item.last_modified_time <= smart_list_item_notion_row.last_edited_time:
                        LOGGER.info(f"Skipping '{smart_list_item_notion_row.name}' because it was not modified")
                        continue

                    smart_list_item_notion_row.name = smart_list_item.name
                    smart_list_item_notion_row.is_done = smart_list_item.is_done
                    smart_list_item_notion_row.url = smart_list_item.url
                    smart_list_item_notion_row.tags = \
                        [all_smart_list_tags_set[t].name for t in smart_list_item.tags]
                    smart_list_item_notion_row.archived = smart_list_item.archived
                    self._notion_manager.save_smart_list_item(
                        smart_list_ref_id, smart_list_item.ref_id, smart_list_item_notion_row)
                    LOGGER.info(f"Changed smart list item '{smart_list_item_notion_row.name}' from local")
                else:
                    raise ServiceError(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random smart list item added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                self._notion_manager.hard_remove_smart_list_item(smart_list_ref_id, notion_smart_list_item_ref_id)
                LOGGER.info(f"Removed smart list item with id={smart_list_item_notion_row.ref_id} from Notion")

        for smart_list_item in all_smart_list_items_rows:
            if smart_list_item.ref_id in smart_list_items_notion_rows_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if smart_list_item.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            self._notion_manager.upsert_smart_list_item(
                smart_list_item, [all_smart_list_tags_set[t].name for t in smart_list_item.tags])
            LOGGER.info(f"Created new smart list item on Notion side '{smart_list_item.name}'")

        # Done this way because it's a bit fasterr
        return all_smart_list_items_set.values()
