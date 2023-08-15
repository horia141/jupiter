"""The command for unsuspending a habit."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class HabitUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class HabitUnsuspendUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitUnsuspendArgs, None]
):
    """The command for unsuspending a habit."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.HABITS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: HabitUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        habit = await uow.habit_repository.load_by_id(args.ref_id)
        habit = habit.unsuspend(
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)
