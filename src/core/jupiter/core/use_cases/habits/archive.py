"""The command for archiving a habit."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
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

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.HABITS

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            habit = await uow.habit_repository.load_by_id(args.ref_id)
        await HabitArchiveService(
            EventSource.CLI,
            self._time_provider,
            self._domain_storage_engine,
        ).do_it(progress_reporter, habit)
