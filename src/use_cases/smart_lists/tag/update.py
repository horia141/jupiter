"""The command for updating a smart list tag."""
from dataclasses import dataclass
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from models.framework import Command, UpdateAction, EntityId
from utils.time_provider import TimeProvider


class SmartListTagUpdateCommand(Command['SmartListTagUpdateCommand.Args', None]):
    """The command for updating a smart list tag."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        tag_name: UpdateAction[SmartListTagName]

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
            smart_list_tag = uow.smart_list_tag_repository.load_by_id(args.ref_id)

            if args.tag_name.should_change:
                smart_list_tag.change_tag_name(args.tag_name.value, self._time_provider.get_current_time())

            uow.smart_list_tag_repository.save(smart_list_tag)

        self._notion_manager.upsert_smart_list_tag(smart_list_tag)
