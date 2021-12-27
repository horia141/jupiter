"""The command for creating a smart list tag."""
from dataclasses import dataclass
from typing import Final

from domain.smart_lists.infra.smart_list_engine import SmartListEngine
from domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from domain.smart_lists.smart_list_tag import SmartListTag
from domain.smart_lists.smart_list_tag_name import SmartListTagName
from domain.smart_lists.smart_list_key import SmartListKey
from framework.use_case import UseCase
from utils.time_provider import TimeProvider


class SmartListTagCreateUseCase(UseCase['SmartListTagCreateUseCase.Args', None]):
    """The command for creating a smart list tag."""

    @dataclass()
    class Args:
        """Args."""
        smart_list_key: SmartListKey
        tag_name: SmartListTagName

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
            metric = uow.smart_list_repository.load_by_key(args.smart_list_key)
            smart_list_tag = SmartListTag.new_smart_list_tag(
                smart_list_ref_id=metric.ref_id, tag_name=args.tag_name,
                created_time=self._time_provider.get_current_time())
            smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
        notion_smart_list_tag = NotionSmartListTag.new_notion_row(smart_list_tag, None)
        self._notion_manager.upsert_smart_list_tag(metric.ref_id, notion_smart_list_tag)
