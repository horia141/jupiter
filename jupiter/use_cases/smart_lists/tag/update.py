"""The command for updating a smart list tag."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class SmartListTagUpdateUseCase(UseCase['SmartListTagUpdateUseCase.Args', None]):
    """The command for updating a smart list tag."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        tag_name: UpdateAction[SmartListTagName]

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
        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_tag = uow.smart_list_tag_repository.load_by_id(args.ref_id)

            smart_list_tag.update(args.tag_name, self._time_provider.get_current_time())

            uow.smart_list_tag_repository.save(smart_list_tag)

        notion_smart_list_tag = \
            self._smart_list_notion_manager.load_smart_list_tag(smart_list_tag.smart_list_ref_id, smart_list_tag.ref_id)
        notion_smart_list_tag = notion_smart_list_tag.join_with_aggregate_root(smart_list_tag, None)
        self._smart_list_notion_manager.save_smart_list_tag(smart_list_tag.smart_list_ref_id, notion_smart_list_tag)
