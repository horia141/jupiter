"""The command for archiving a smart list."""
import logging
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, \
    NotionSmartListNotFoundError
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListArchiveUseCase(UseCase[SmartListKey, None]):
    """The command for archiving a smart list."""

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

    def execute(self, args: SmartListKey) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.load_by_key(args)

            for smart_list_tag in uow.smart_list_tag_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_tag.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.smart_list_tag_repository.save(smart_list_tag)

            for smart_list_item in uow.smart_list_item_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_item.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

            smart_list.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.smart_list_repository.save(smart_list)
            LOGGER.info("Applied local changes")

        try:
            self._smart_list_notion_manager.remove_smart_list(smart_list.ref_id)
            LOGGER.info("Applied Notion changes")
        except NotionSmartListNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
