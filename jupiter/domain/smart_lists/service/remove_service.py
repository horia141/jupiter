"""Shared service for removing a metric."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
    NotionSmartListNotFoundError,
)
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.storage_engine import DomainStorageEngine

LOGGER = logging.getLogger(__name__)


class SmartListRemoveService:
    """Shared service for removing a smart list."""

    _storage_engine: Final[DomainStorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
        self,
        storage_engine: DomainStorageEngine,
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def execute(
        self, smart_list_collection: SmartListCollection, smart_list: SmartList
    ) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            all_smart_list_tags = uow.smart_list_tag_repository.find_all(
                smart_list.ref_id, allow_archived=True
            )
            for smart_list_tag in all_smart_list_tags:
                uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)

            all_smart_list_items = uow.smart_list_item_repository.find_all(
                smart_list.ref_id, allow_archived=True
            )
            for smart_list_item in all_smart_list_items:
                uow.smart_list_item_repository.remove(smart_list_item.ref_id)

            uow.smart_list_repository.remove(smart_list.ref_id)
            LOGGER.info("Applied local changes")

        try:
            self._smart_list_notion_manager.drop_all_branch_tags(
                smart_list_collection.ref_id, smart_list.ref_id
            )
            self._smart_list_notion_manager.drop_all_leaves(
                smart_list_collection.ref_id, smart_list.ref_id
            )
            self._smart_list_notion_manager.remove_branch(
                smart_list_collection.ref_id, smart_list.ref_id
            )
            LOGGER.info("Applied remote changes")
        except NotionSmartListNotFoundError:
            LOGGER.warning(
                "Skipping archival on Notion side because smart_list was not found"
            )
