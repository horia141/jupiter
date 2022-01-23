"""The command for creating a smart list tag."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class SmartListTagCreateUseCase(UseCase['SmartListTagCreateUseCase.Args', None]):
    """The command for creating a smart list tag."""

    @dataclass()
    class Args:
        """Args."""
        smart_list_key: SmartListKey
        tag_name: SmartListTagName

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._smart_list_notion_manager = smart_list_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric = uow.smart_list_repository.load_by_key(args.smart_list_key)
            smart_list_tag = SmartListTag.new_smart_list_tag(
                smart_list_ref_id=metric.ref_id, tag_name=args.tag_name, source=EventSource.CLI,
                created_time=self._time_provider.get_current_time())
            smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)
        notion_smart_list_tag = NotionSmartListTag.new_notion_row(smart_list_tag, None)
        self._smart_list_notion_manager.upsert_smart_list_tag(metric.ref_id, notion_smart_list_tag)
