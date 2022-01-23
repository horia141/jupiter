"""The command for updating a smart list."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class SmartListUpdateUseCase(UseCase['SmartListUpdateUseCase.Args', None]):
    """The command for updating a smart list."""

    @dataclass()
    class Args:
        """Args."""
        key: SmartListKey
        name: UpdateAction[SmartListName]

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
            smart_list = uow.smart_list_repository.load_by_key(args.key)

            smart_list = smart_list.update(args.name, EventSource.CLI, self._time_provider.get_current_time())

            uow.smart_list_repository.save(smart_list)

        notion_smart_list = self._smart_list_notion_manager.load_smart_list(smart_list.ref_id)
        notion_smart_list = notion_smart_list.join_with_aggregate_root(smart_list)
        self._smart_list_notion_manager.save_smart_list(notion_smart_list)
