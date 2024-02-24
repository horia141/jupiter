"""The command for archiving a habit."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.service.archive_service import HabitArchiveService
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
class HabitArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitArchiveArgs, None]
):
    """The command for archiving a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        habit = await uow.repository_for(Habit).load_by_id(args.ref_id)
        await HabitArchiveService().do_it(
            context.domain_context, uow, progress_reporter, habit
        )
