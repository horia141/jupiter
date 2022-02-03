"""The command for updating a smart list."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class SmartListUpdateUseCase(AppMutationUseCase['SmartListUpdateUseCase.Args', None]):
    """The command for updating a smart list."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: SmartListKey
        name: UpdateAction[SmartListName]

    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            smart_list_notion_manager: SmartListNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            smart_list_collection = uow.smart_list_collection_repository.load_by_workspace(workspace.ref_id)

            smart_list = uow.smart_list_repository.load_by_key(smart_list_collection.ref_id, args.key)

            smart_list = smart_list.update(args.name, EventSource.CLI, self._time_provider.get_current_time())

            uow.smart_list_repository.save(smart_list)

        notion_smart_list = \
            self._smart_list_notion_manager.load_smart_list(smart_list_collection.ref_id, smart_list.ref_id)
        notion_smart_list = notion_smart_list.join_with_aggregate_root(smart_list)
        self._smart_list_notion_manager.save_smart_list(smart_list_collection.ref_id, notion_smart_list)
