"""Shared service for removing a metric."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
    NotionSmartListNotFoundError,
    NotionSmartListItemNotFoundError,
    NotionSmartListTagNotFoundError,
)
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.use_case import ProgressReporter, MarkProgressStatus

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
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
    ) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            all_smart_list_tags = uow.smart_list_tag_repository.find_all(
                smart_list.ref_id, allow_archived=True
            )
            all_smart_list_items = uow.smart_list_item_repository.find_all(
                smart_list.ref_id, allow_archived=True
            )

        for smart_list_tag in all_smart_list_tags:
            with progress_reporter.start_removing_entity(
                "smart list tag", smart_list_tag.ref_id, str(smart_list_tag.tag_name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)
                    entity_reporter.mark_local_change()

                try:
                    self._smart_list_notion_manager.remove_branch_tag(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_tag.ref_id,
                    )
                except NotionSmartListTagNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because smart list tag was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        for smart_list_item in all_smart_list_items:
            with progress_reporter.start_removing_entity(
                "smart list item", smart_list_item.ref_id, str(smart_list_item.name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.smart_list_item_repository.remove(smart_list_item.ref_id)
                    entity_reporter.mark_local_change()

                try:
                    self._smart_list_notion_manager.remove_leaf(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_item.ref_id,
                    )
                    entity_reporter.mark_remote_change()
                except NotionSmartListItemNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because smart list item was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        with progress_reporter.start_removing_entity(
            "smart list", smart_list.ref_id
        ) as entity_reporter:
            entity_reporter.mark_known_name(str(smart_list.name))
            with self._storage_engine.get_unit_of_work() as uow:
                uow.smart_list_repository.remove(smart_list.ref_id)
                entity_reporter.mark_local_change()

            try:
                self._smart_list_notion_manager.drop_all_branch_tags(
                    smart_list_collection.ref_id, smart_list.ref_id
                )
                entity_reporter.mark_other_progress("tags")
                self._smart_list_notion_manager.remove_branch(
                    smart_list_collection.ref_id, smart_list.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionSmartListNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because smart list was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
