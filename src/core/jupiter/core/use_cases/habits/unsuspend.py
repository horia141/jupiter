"""The command for unsuspending a habit."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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
class HabitUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitUnsuspendUseCase(AppLoggedInMutationUseCase[HabitUnsuspendArgs, None]):
    """The command for unsuspending a habit."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.HABITS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        async with progress_reporter.start_updating_entity(
            "habit",
            args.ref_id,
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                habit = await uow.habit_repository.load_by_id(args.ref_id)
                await entity_reporter.mark_known_name(str(habit.name))
                habit = habit.unsuspend(
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await uow.habit_repository.save(habit)
                await entity_reporter.mark_local_change()
