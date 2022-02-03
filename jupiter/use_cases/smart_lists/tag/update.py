"""The command for updating a smart list tag."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class SmartListTagUpdateUseCase(AppMutationUseCase['SmartListTagUpdateUseCase.Args', None]):
    """The command for updating a smart list tag."""

    @dataclass()
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId
        tag_name: UpdateAction[SmartListTagName]

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

            smart_list_tag = uow.smart_list_tag_repository.load_by_id(args.ref_id)

            smart_list_tag = \
                smart_list_tag.update(
                    tag_name=args.tag_name, source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time())

            uow.smart_list_tag_repository.save(smart_list_tag)

        notion_smart_list_tag = \
            self._smart_list_notion_manager.load_smart_list_tag(
                smart_list_collection.ref_id, smart_list_tag.smart_list_ref_id, smart_list_tag.ref_id)
        notion_smart_list_tag = notion_smart_list_tag.join_with_aggregate_root(smart_list_tag, None)
        self._smart_list_notion_manager.save_smart_list_tag(
            smart_list_collection.ref_id, smart_list_tag.smart_list_ref_id, notion_smart_list_tag)
