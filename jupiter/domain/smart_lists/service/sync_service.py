"""Shared service for syncing smart lists."""
import logging
from typing import Final, Optional, Iterable

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListNotFoundError, NotionSmartListTagNotFoundError, NotionSmartListItemNotFoundError
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_item import NotionSmartListItem
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp

LOGGER = logging.getLogger(__name__)


class SmartListSyncService:
    """The service class for syncing smart lists."""

    _storage_engine: Final[DomainStorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, storage_engine: DomainStorageEngine, smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def sync(
            self,
            workspace: Workspace,
            right_now: Timestamp,
            smart_list: SmartList,
            drop_all_notion_side: bool,
            sync_even_if_not_modified: bool,
            filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer) -> Iterable[SmartListItem]:
        """Synchronise a smart list and its items between Notion and local storage."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_workspace(workspace.ref_id)

        try:
            notion_smart_list = \
                self._smart_list_notion_manager.load_smart_list(smart_list_collection.ref_id, smart_list.ref_id)

            if sync_prefer == SyncPrefer.LOCAL:
                notion_smart_list = notion_smart_list.join_with_aggregate_root(smart_list)
                self._smart_list_notion_manager.save_smart_list(smart_list_collection.ref_id, notion_smart_list)
                LOGGER.info("Applied changes to Notion")
            elif sync_prefer == SyncPrefer.NOTION:
                smart_list = notion_smart_list.apply_to_aggregate_root(smart_list, right_now)
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.smart_list_repository.save(smart_list)
                LOGGER.info("Applied local change")
            else:
                raise Exception(f"Invalid preference {sync_prefer}")
        except NotionSmartListNotFoundError:
            LOGGER.info("Trying to recreate the smart list")
            notion_smart_list = NotionSmartList.new_notion_row(smart_list)
            self._smart_list_notion_manager.upsert_smart_list(smart_list_collection.ref_id, notion_smart_list)

        # Synchronise the tags here.
        with self._storage_engine.get_unit_of_work() as uow:
            all_smart_list_tags = \
                uow.smart_list_tag_repository.find_all(smart_list_ref_id=smart_list.ref_id, allow_archived=True)
        all_smart_list_tags_set = {slt.ref_id: slt for slt in all_smart_list_tags}
        all_smart_list_tags_by_name = {slt.tag_name: slt for slt in all_smart_list_tags}

        if not drop_all_notion_side:
            all_notion_smart_list_tags = \
                self._smart_list_notion_manager.load_all_smart_list_tags(
                    smart_list_collection.ref_id, smart_list.ref_id)
            all_notion_smart_list_tags_notion_ids = \
                set(self._smart_list_notion_manager.load_all_saved_smart_list_tags_notion_ids(
                    smart_list_collection.ref_id, smart_list.ref_id))
        else:
            self._smart_list_notion_manager.drop_all_smart_list_tags(smart_list_collection.ref_id, smart_list.ref_id)
            all_notion_smart_list_tags = []
            all_notion_smart_list_tags_notion_ids = set()
        notion_smart_list_tags_set = {}

        for notion_smart_list_tag in all_notion_smart_list_tags:
            LOGGER.info(f"Syncing tag '{notion_smart_list_tag.name}' (id={notion_smart_list_tag.notion_id})")

            if notion_smart_list_tag.ref_id is None:
                # If the smart list tag doesn't exist locally, we create it.
                new_smart_list_tag = \
                    notion_smart_list_tag.new_aggregate_root(NotionSmartListTag.InverseInfo(smart_list.ref_id))
                with self._storage_engine.get_unit_of_work() as uow:
                    new_smart_list_tag = uow.smart_list_tag_repository.create(new_smart_list_tag)
                LOGGER.info(f"Found new smart list tag from Notion '{new_smart_list_tag.tag_name}'")

                self._smart_list_notion_manager.link_local_and_notion_tag_for_smart_list(
                    smart_list_collection.ref_id, smart_list.ref_id, new_smart_list_tag.ref_id,
                    notion_smart_list_tag.notion_id)
                LOGGER.info("Linked the new smart list tag with local entries")

                notion_smart_list_tag = notion_smart_list_tag.join_with_aggregate_root(new_smart_list_tag, None)
                self._smart_list_notion_manager.save_smart_list_tag(
                    smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_tag)
                LOGGER.info("Applied changes on Notion side too")

                notion_smart_list_tags_set[new_smart_list_tag.ref_id] = notion_smart_list_tag
                all_smart_list_tags.append(new_smart_list_tag)
                all_smart_list_tags_set[new_smart_list_tag.ref_id] = new_smart_list_tag
                all_smart_list_tags_by_name[new_smart_list_tag.tag_name] = new_smart_list_tag
            elif notion_smart_list_tag.ref_id in all_smart_list_tags_set and \
                    notion_smart_list_tag.notion_id in all_notion_smart_list_tags_notion_ids:
                smart_list_tag = all_smart_list_tags_set[notion_smart_list_tag.ref_id]
                notion_smart_list_tags_set[notion_smart_list_tag.ref_id] = notion_smart_list_tag

                if sync_prefer == SyncPrefer.NOTION:
                    updated_smart_list_tag = \
                        notion_smart_list_tag.apply_to_aggregate_root(
                            smart_list_tag, NotionSmartListTag.InverseInfo(smart_list.ref_id))
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.smart_list_tag_repository.save(updated_smart_list_tag)
                    all_smart_list_tags_set[notion_smart_list_tag.ref_id] = updated_smart_list_tag
                    all_smart_list_tags_by_name[smart_list_tag.tag_name] = updated_smart_list_tag
                    LOGGER.info(f"Changed smart list tag '{smart_list_tag.tag_name}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    updated_notion_smart_list_tag = \
                        notion_smart_list_tag.join_with_aggregate_root(smart_list_tag, None)
                    self._smart_list_notion_manager.save_smart_list_tag(
                        smart_list_collection.ref_id, smart_list.ref_id, updated_notion_smart_list_tag)
                    LOGGER.info(f"Changed smart list tag '{notion_smart_list_tag.name}' from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random smart list tag added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._smart_list_notion_manager.remove_smart_list_tag(
                        smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_tag.ref_id)
                    LOGGER.info(f"Removed smart list item with id={notion_smart_list_tag.ref_id} from Notion")
                except NotionSmartListTagNotFoundError:
                    LOGGER.info(f"Skipped dangling smart list item in Notion {notion_smart_list_tag.ref_id}")

        for smart_list_tag in all_smart_list_tags:
            if smart_list_tag.ref_id in notion_smart_list_tags_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if smart_list_tag.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            notion_smart_list_tag = NotionSmartListTag.new_notion_row(smart_list_tag, None)
            self._smart_list_notion_manager.upsert_smart_list_tag(
                smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_tag)
            LOGGER.info(f"Created new smart list tag on Notion side '{smart_list_tag.tag_name}'")

        # Now synchronize the list items here.
        filter_smart_list_item_ref_ids_set = frozenset(filter_smart_list_item_ref_ids) \
            if filter_smart_list_item_ref_ids else None

        with self._storage_engine.get_unit_of_work() as uow:
            all_smart_list_items = \
                uow.smart_list_item_repository.find_all(
                    smart_list_ref_id=smart_list.ref_id,
                    allow_archived=True,
                    filter_ref_ids=filter_smart_list_item_ref_ids)
        all_smart_list_items_set = {sli.ref_id: sli for sli in all_smart_list_items}

        if not drop_all_notion_side:
            all_notion_smart_list_items = \
                self._smart_list_notion_manager.load_all_smart_list_items(
                    smart_list_collection.ref_id, smart_list.ref_id)
            all_notion_smart_list_items_notion_ids = \
                set(self._smart_list_notion_manager.load_all_saved_smart_list_items_notion_ids(
                    smart_list_collection.ref_id, smart_list.ref_id))
        else:
            self._smart_list_notion_manager.drop_all_smart_list_items(smart_list_collection.ref_id, smart_list.ref_id)
            all_notion_smart_list_items = []
            all_notion_smart_list_items_notion_ids = set()
        all_notion_smart_list_items_set = {}

        # Explore Notion and apply to local
        for notion_smart_list_item in all_notion_smart_list_items:
            if filter_smart_list_item_ref_ids_set is not None and \
                    notion_smart_list_item.ref_id not in filter_smart_list_item_ref_ids_set:
                LOGGER.info(f"Skipping '{notion_smart_list_item.name}' (id={notion_smart_list_item.notion_id})")
                continue

            LOGGER.info(f"Syncing '{notion_smart_list_item.name}' (id={notion_smart_list_item.notion_id})")

            if notion_smart_list_item.ref_id is None:
                # If the smart list item doesn't exist locally, we create it.
                new_smart_list_item = notion_smart_list_item.new_aggregate_root(
                    NotionSmartListItem.InverseInfo(smart_list.ref_id, all_smart_list_tags_by_name))

                with self._storage_engine.get_unit_of_work() as uow:
                    new_smart_list_item = uow.smart_list_item_repository.create(new_smart_list_item)
                LOGGER.info(f"Found new smart list item from Notion '{new_smart_list_item.name}'")

                self._smart_list_notion_manager.link_local_and_notion_entries_for_smart_list(
                    smart_list_collection.ref_id, smart_list.ref_id, new_smart_list_item.ref_id,
                    notion_smart_list_item.notion_id)
                LOGGER.info("Linked the new smart list item with local entries")

                notion_smart_list_item = notion_smart_list_item.join_with_aggregate_root(
                    new_smart_list_item, NotionSmartListItem.DirectInfo(all_smart_list_tags_set))
                self._smart_list_notion_manager.save_smart_list_item(
                    smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_item)
                LOGGER.info("Applied changes on Notion side too")

                all_smart_list_items_set[new_smart_list_item.ref_id] = new_smart_list_item
                all_notion_smart_list_items_set[new_smart_list_item.ref_id] = \
                    notion_smart_list_item
            elif notion_smart_list_item.ref_id in all_smart_list_items_set and \
                    notion_smart_list_item.notion_id in all_notion_smart_list_items_notion_ids:
                smart_list_item = all_smart_list_items_set[notion_smart_list_item.ref_id]
                all_notion_smart_list_items_set[notion_smart_list_item.ref_id] = \
                    notion_smart_list_item

                if sync_prefer == SyncPrefer.NOTION:
                    if not sync_even_if_not_modified and \
                            notion_smart_list_item.last_edited_time <= smart_list_item.last_modified_time:
                        LOGGER.info(f"Skipping '{notion_smart_list_item.name}' because it was not modified")
                        continue

                    updated_smart_list_item = notion_smart_list_item.apply_to_aggregate_root(
                        smart_list_item,
                        NotionSmartListItem.InverseInfo(smart_list.ref_id, all_smart_list_tags_by_name))
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.smart_list_item_repository.save(updated_smart_list_item)
                    all_smart_list_items_set[notion_smart_list_item.ref_id] = updated_smart_list_item
                    LOGGER.info(f"Changed smart list item '{smart_list_item.name}' from Notion")
                elif sync_prefer == SyncPrefer.LOCAL:
                    if not sync_even_if_not_modified and \
                            smart_list_item.last_modified_time <= notion_smart_list_item.last_edited_time:
                        LOGGER.info(f"Skipping '{notion_smart_list_item.name}' because it was not modified")
                        continue

                    updated_notion_smart_list_item = notion_smart_list_item.join_with_aggregate_root(
                        smart_list_item, NotionSmartListItem.DirectInfo(all_smart_list_tags_set))
                    self._smart_list_notion_manager.save_smart_list_item(
                        smart_list_collection.ref_id, smart_list.ref_id, updated_notion_smart_list_item)
                    all_notion_smart_list_items_set[notion_smart_list_item.ref_id] = updated_notion_smart_list_item
                    LOGGER.info(f"Changed smart list item '{notion_smart_list_item.name}' from local")
                else:
                    raise Exception(f"Invalid preference {sync_prefer}")
            else:
                # If we're here, one of two cases have happened:
                # 1. This is some random smart list item added by someone, where they completed themselves a ref_id.
                #    It's a bad setup, and we remove it.
                # 2. This is a smart list item added by the script, but which failed before local data could be saved.
                #    We'll have duplicates in these cases, and they need to be removed.
                try:
                    self._smart_list_notion_manager.remove_smart_list_item(
                        smart_list_collection.ref_id, smart_list.ref_id, smart_list_item.ref_id)
                    LOGGER.info(f"Removed smart list item with id={notion_smart_list_item.ref_id} from Notion")
                except NotionSmartListItemNotFoundError:
                    LOGGER.info(f"Skipped dangling smart list item in Notion {notion_smart_list_item.ref_id}")

        for smart_list_item in all_smart_list_items:
            if smart_list_item.ref_id in all_notion_smart_list_items_set:
                # The smart list item already exists on Notion side, so it was handled by the above loop!
                continue
            if smart_list_item.archived:
                continue

            # If the smart list item does not exist on Notion side, we create it.
            notion_smart_list_item = \
                NotionSmartListItem.new_notion_row(
                    smart_list_item, NotionSmartListItem.DirectInfo(all_smart_list_tags_set))
            self._smart_list_notion_manager.upsert_smart_list_item(
                smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_item)
            all_notion_smart_list_items_set[smart_list_item.ref_id] = notion_smart_list_item
            LOGGER.info(f"Created new smart list item on Notion side '{smart_list_item.name}'")

        # Done this way because it's a bit fasterr
        return all_smart_list_items_set.values()
