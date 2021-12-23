"""The command for removing a smart list tag."""
import logging
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from framework.entity_id import EntityId
from framework.use_case import UseCase
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SmartListTagRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a smart list tag."""

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

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._smart_list_engine.get_unit_of_work() as uow:
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
            self._notion_manager.remove_smart_list_tag(smart_list_tag.smart_list_ref_id, smart_list_tag.ref_id)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
