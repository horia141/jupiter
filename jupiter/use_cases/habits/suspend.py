"""The command for suspend a habit."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import MutationUseCaseInvocationRecorder, UseCaseArgsBase
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class HabitSuspendUseCase(AppMutationUseCase['HabitSuspendUseCase.Args', None]):
    """The command for suspending a habit."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _habit_notion_manager: Final[HabitNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            habit_notion_manager: HabitNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._habit_notion_manager = habit_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            habit = uow.habit_repository.load_by_id(args.ref_id)
            project = uow.project_repository.load_by_id(habit.project_ref_id)
            habit = habit.suspend(source=EventSource.CLI, modification_time=self._time_provider.get_current_time())
            uow.habit_repository.save(habit)

        direct_info = NotionHabit.DirectInfo(project_name=project.name)
        notion_habit = self._habit_notion_manager.load_habit(habit.habit_collection_ref_id, habit.ref_id)
        notion_habit = notion_habit.join_with_aggregate_root(habit, direct_info)
        self._habit_notion_manager.save_habit(habit.habit_collection_ref_id, notion_habit)
