"""The command for updating a smart list."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.smart_lists.smart_list_name import SmartListName
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class SmartListUpdateUseCase(AppMutationUseCase["SmartListUpdateUseCase.Args", None]):
    """The command for updating a smart list."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        key: SmartListKey
        name: UpdateAction[SmartListName]
        icon: UpdateAction[Optional[EntityIcon]]

    _smart_list_notion_manager: Final[SmartListNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        smart_list_notion_manager: SmartListNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._smart_list_notion_manager = smart_list_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with progress_reporter.start_updating_entity("smart list") as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                smart_list_collection = (
                    uow.smart_list_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )

                smart_list = uow.smart_list_repository.load_by_key(
                    smart_list_collection.ref_id, args.key
                )
                entity_reporter.mark_known_entity_id(smart_list.ref_id)

                smart_list = smart_list.update(
                    name=args.name,
                    icon=args.icon,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(smart_list.name))

                uow.smart_list_repository.save(smart_list)
                entity_reporter.mark_local_change()

            notion_smart_list = self._smart_list_notion_manager.load_branch(
                smart_list_collection.ref_id, smart_list.ref_id
            )
            notion_smart_list = notion_smart_list.join_with_entity(smart_list)
            self._smart_list_notion_manager.save_branch(
                smart_list_collection.ref_id, notion_smart_list
            )
            entity_reporter.mark_remote_change()
