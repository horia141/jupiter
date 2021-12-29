"""The command for creating a smart list."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.entity_name import EntityName
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class SmartListCreateUseCase(UseCase['SmartListCreateUseCase.Args', None]):
    """The command for creating a smart list."""

    @dataclass()
    class Args:
        """Args."""
        key: SmartListKey
        name: EntityName

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

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        smart_list = SmartList.new_smart_list(
            args.key, args.name, self._time_provider.get_current_time())
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list = uow.smart_list_repository.create(smart_list)
            smart_list_default_tag = SmartListTag.new_smart_list_tag(
                smart_list.ref_id, SmartListTagName('Default'), self._time_provider.get_current_time())
            smart_list_default_tag = uow.smart_list_tag_repository.create(smart_list_default_tag)
        notion_smart_list = NotionSmartList.new_notion_row(smart_list)
        self._smart_list_notion_manager.upsert_smart_list(notion_smart_list)
        notion_smart_list_default_tag = NotionSmartListTag.new_notion_row(smart_list_default_tag, None)
        self._smart_list_notion_manager.upsert_smart_list_tag(smart_list.ref_id, notion_smart_list_default_tag)
