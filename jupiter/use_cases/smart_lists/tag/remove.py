"""The command for removing a smart list tag."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListTagNotFoundError
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListTagRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a smart list tag."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_tag = uow.smart_list_tag_repository.remove(args)

            smart_list_items = uow.smart_list_item_repository.find_all(
                allow_archived=True,
                filter_smart_list_ref_ids=[smart_list_tag.smart_list_ref_id],
                filter_tag_ref_ids=[args])

            for smart_list_item in smart_list_items:
                smart_list_item.change_tags(
                    [t for t in smart_list_item.tags if t != args], self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

        try:
            self._smart_list_notion_manager.remove_smart_list_tag(
                smart_list_tag.smart_list_ref_id, smart_list_tag.ref_id)
        except NotionSmartListTagNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")