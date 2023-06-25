"""The command for suspend a habit."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class HabitSuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitSuspendUseCase(AppLoggedInMutationUseCase[HabitSuspendArgs, None]):
    """The command for suspending a habit."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitSuspendArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "habit",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                habit = await uow.habit_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(habit.name))
                habit = habit.suspend(
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await uow.habit_repository.save(habit)
                await entity_reporter.mark_local_change()
