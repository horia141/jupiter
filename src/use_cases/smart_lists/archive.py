"""The command for archiving a smart list."""
import logging
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, NotionSmartListNotFoundError
from domain.smart_lists.smart_list_key import SmartListKey
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListArchiveUseCase(UseCase[SmartListKey, None]):
    """The command for archiving a smart list."""

    _time_provider: Final[TimeProvider]
    _smart_list_engine: Final[SmartListEngine]
    _notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, smart_list_engine: SmartListEngine,
            notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._smart_list_engine = smart_list_engine
        self._notion_manager = notion_manager

    def execute(self, args: SmartListKey) -> None:
        """Execute the command's action."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.load_by_key(args)

            for smart_list_tag in uow.smart_list_tag_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_tag.mark_archived(archived_time=self._time_provider.get_current_time())
                uow.smart_list_tag_repository.save(smart_list_tag)

            for smart_list_item in uow.smart_list_item_repository.find_all_for_smart_list(smart_list.ref_id):
                smart_list_item.mark_archived(archived_time=self._time_provider.get_current_time())
                uow.smart_list_item_repository.save(smart_list_item)

            smart_list.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.smart_list_repository.save(smart_list)
            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.remove_smart_list(smart_list.ref_id)
            LOGGER.info("Applied Notion changes")
        except NotionSmartListNotFoundError:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
