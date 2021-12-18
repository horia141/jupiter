"""The command for removing a smart list item."""
import logging
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from models.framework import Command, EntityId
from remote.notion.common import CollectionEntityNotFound


LOGGER = logging.getLogger(__name__)


class SmartListItemRemoveCommand(Command[EntityId, None]):
    """The command for removing a smart list item."""

    _smart_list_engine: Final[SmartListEngine]
    _notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, smart_list_engune: SmartListEngine, notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._smart_list_engine = smart_list_engune
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list_item = uow.smart_list_item_repository.remove(args)

        try:
            self._notion_manager.remove_smart_list_item(smart_list_item)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because smart list was not found")
