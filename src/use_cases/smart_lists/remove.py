"""The command for hard removing a smart list."""
import logging
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager, NotionSmartListNotFoundError
from domain.smart_lists.smart_list_key import SmartListKey
from framework.use_case import UseCase
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListRemoveUseCase(UseCase[SmartListKey, None]):
    """The command for removing a smart list."""

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

            for smart_list_tag in uow.smart_list_tag_repository.find_all_for_smart_list(
                    smart_list.ref_id, allow_archived=True):
                uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)

            for smart_list_entry in uow.smart_list_item_repository.find_all_for_smart_list(
                    smart_list.ref_id, allow_archived=True):
                uow.smart_list_item_repository.remove(smart_list_entry.ref_id)

            uow.smart_list_repository.remove(smart_list.ref_id)
            LOGGER.info("Applied local changes")

        try:
            self._notion_manager.remove_smart_list(smart_list.ref_id)
            LOGGER.info("Applied remote changes")
        except NotionSmartListNotFoundError:
            LOGGER.warning("Skipping archival on Notion side because smart_list was not found")
