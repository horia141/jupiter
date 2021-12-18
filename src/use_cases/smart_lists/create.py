"""The command for creating a smart list."""
from dataclasses import dataclass
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.smart_list import SmartList
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from domain.entity_name import EntityName
from domain.smart_lists.smart_list_key import SmartListKey
from models.framework import Command
from utils.time_provider import TimeProvider


class SmartListCreateCommand(Command['SmartListCreateCommand.Args', None]):
    """The command for creating a smart list."""

    @dataclass()
    class Args:
        """Args."""
        key: SmartListKey
        name: EntityName

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

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        smart_list = SmartList.new_smart_list(
            args.key, args.name, self._time_provider.get_current_time())
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.create(smart_list)
            smart_list_default_tag = SmartListTag.new_smart_list_tag(
                smart_list.ref_id, SmartListTagName('Default'), self._time_provider.get_current_time())
            smart_list_default_tag = uow.smart_list_tag_repository.create(smart_list_default_tag)
        self._notion_manager.upsert_smart_list(smart_list)
        self._notion_manager.upsert_smart_list_tag(smart_list_default_tag)
