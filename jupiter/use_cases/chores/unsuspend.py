"""The command for unsuspending a chore."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
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


class ChoreUnsuspendUseCase(AppMutationUseCase["ChoreUnsuspendUseCase.Args", None]):
    """The command for unsuspending a chore."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId

    _chore_notion_manager: Final[ChoreNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        chore_notion_manager: ChoreNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._chore_notion_manager = chore_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        with progress_reporter.start_updating_entity(
            "chore", args.ref_id
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                chore = uow.chore_repository.load_by_id(args.ref_id)
                entity_reporter.mark_known_name(str(chore.name))
                project = uow.project_repository.load_by_id(chore.project_ref_id)
                chore = chore.unsuspend(
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                uow.chore_repository.save(chore)
                entity_reporter.mark_local_change()

            direct_info = NotionChore.DirectInfo(
                all_projects_map={project.ref_id: project}
            )
            notion_chore = self._chore_notion_manager.load_leaf(
                chore.chore_collection_ref_id, chore.ref_id
            )
            notion_chore = notion_chore.join_with_entity(chore, direct_info)
            self._chore_notion_manager.save_leaf(
                chore.chore_collection_ref_id, notion_chore
            )
            entity_reporter.mark_remote_change()
