"""The command for unsuspending a habit."""
from dataclasses import dataclass

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@dataclass
class HabitUnsuspendArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitUnsuspendUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitUnsuspendArgs, None]
):
    """The command for unsuspending a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitUnsuspendArgs,
    ) -> None:
        """Execute the command's action."""
        habit = await uow.habit_repository.load_by_id(args.ref_id)
        habit = habit.unsuspend(context.domain_context)
        await uow.habit_repository.save(habit)
        await progress_reporter.mark_updated(habit)
