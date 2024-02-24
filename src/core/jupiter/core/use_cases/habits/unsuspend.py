"""The command for unsuspending a habit."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
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
        habit = await uow.repository_for(Habit).load_by_id(args.ref_id)
        habit = habit.unsuspend(context.domain_context)
        await uow.repository_for(Habit).save(habit)
        await progress_reporter.mark_updated(habit)
