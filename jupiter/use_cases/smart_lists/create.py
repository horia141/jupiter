"""The command for creating a smart list."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list import NotionSmartList
from jupiter.domain.smart_lists.notion_smart_list_tag import NotionSmartListTag
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.domain.smart_lists.smart_list_tag_name import SmartListTagName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class SmartListCreateUseCase(AppMutationUseCase['SmartListCreateUseCase.Args', None]):
    """The command for creating a smart list."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: SmartListKey
        name: SmartListName

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

            smart_list = \
                SmartList.new_smart_list(
                    smart_list_collection_ref_id=smart_list_collection.ref_id, key=args.key, name=args.name,
                    source=EventSource.CLI, created_time=self._time_provider.get_current_time())

            smart_list = uow.smart_list_repository.create(smart_list)
            smart_list_default_tag = SmartListTag.new_smart_list_tag(
                smart_list_ref_id=smart_list.ref_id, tag_name=SmartListTagName('Default'),
                source=EventSource.CLI, created_time=self._time_provider.get_current_time())
            smart_list_default_tag = uow.smart_list_tag_repository.create(smart_list_default_tag)

        notion_smart_list = NotionSmartList.new_notion_row(smart_list)
        self._smart_list_notion_manager.upsert_smart_list(smart_list_collection.ref_id, notion_smart_list)
        notion_smart_list_default_tag = NotionSmartListTag.new_notion_row(smart_list_default_tag, None)
        self._smart_list_notion_manager.upsert_smart_list_tag(
            smart_list_collection.ref_id, smart_list.ref_id, notion_smart_list_default_tag)
