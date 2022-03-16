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
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class SmartListTagCreateUseCase(AppMutationUseCase['SmartListTagCreateUseCase.Args', None]):
    """The command for creating a smart list tag."""

    @dataclass()
    class Args(UseCaseArgsBase):
        """Args."""
        smart_list_key: SmartListKey
        tag_name: SmartListTagName

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
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(workspace.ref_id)

            metric = uow.smart_list_repository.load_by_key(smart_list_collection.ref_id, args.smart_list_key)
            smart_list_tag = \
                SmartListTag.new_smart_list_tag(
                    smart_list_ref_id=metric.ref_id, tag_name=args.tag_name, source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time())
            smart_list_tag = uow.smart_list_tag_repository.create(smart_list_tag)

        notion_smart_list_tag = NotionSmartListTag.new_notion_entity(smart_list_tag)
        self._smart_list_notion_manager.upsert_branch_tag(
            smart_list_collection.ref_id, metric.ref_id, notion_smart_list_tag)
