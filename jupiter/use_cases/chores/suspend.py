"""The command for suspend a chore."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class ChoreSuspendUseCase(AppMutationUseCase['ChoreSuspendUseCase.Args', None]):
    """The command for suspending a chore."""

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
            chore_notion_manager: ChoreNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._chore_notion_manager = chore_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            chore = uow.chore_repository.load_by_id(args.ref_id)
            project = uow.project_repository.load_by_id(chore.project_ref_id)
            chore = chore.suspend(source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.chore_repository.save(chore)

        direct_info = NotionChore.DirectInfo(project_name=project.name)
        notion_chore = self._chore_notion_manager.load_chore(chore.chore_collection_ref_id, chore.ref_id)
        notion_chore = notion_chore.join_with_entity(chore, direct_info)
        self._chore_notion_manager.save_chore(chore.chore_collection_ref_id, notion_chore)
