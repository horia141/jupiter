"""The command for archiving a smart list item."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListItemNotFoundError
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListItemArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a smart list item."""

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
            smart_list_item = uow.smart_list_item_repository.load_by_id(args)
            smart_list_item.mark_archived(self._time_provider.get_current_time())
            uow.smart_list_item_repository.save(smart_list_item)

        try:
            self._smart_list_notion_manager.remove_smart_list_item(
                smart_list_item.smart_list_ref_id, smart_list_item.ref_id)
        except NotionSmartListItemNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
