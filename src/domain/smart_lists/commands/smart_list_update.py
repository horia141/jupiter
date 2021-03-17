"""The command for updating a smart list."""
from dataclasses import dataclass
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from models.basic import SmartListKey, EntityName
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider


class SmartListUpdateCommand(Command['SmartListUpdateCommand.Args', None]):
    """The command for updating a smart list."""

    @dataclass()
    class Args:
        """Args."""
        key: SmartListKey
        name: UpdateAction[EntityName]

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
        with self._smart_list_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.get_by_key(args.key)

            if args.name.should_change:
                smart_list.change_name(args.name.value, self._time_provider.get_current_time())

            uow.smart_list_repository.save(smart_list)

        self._notion_manager.upsert_smart_list(smart_list)
