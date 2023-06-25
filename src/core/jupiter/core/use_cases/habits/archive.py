"""The command for archiving a habit."""
from dataclasses import dataclass

from jupiter.core.domain.habits.service.archive_service import HabitArchiveService
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
class HabitArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitArchiveUseCase(AppLoggedInMutationUseCase[HabitArchiveArgs, None]):
    """The command for archiving a habit."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            habit = await uow.habit_repository.load_by_id(args.ref_id)
        await HabitArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._storage_engine,
        ).do_it(progress_reporter, habit)
