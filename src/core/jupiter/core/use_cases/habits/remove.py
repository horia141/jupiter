"""The command for removing a habit."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.habits.service.remove_service import HabitRemoveService
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
class HabitRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.HABITS)
class HabitRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[HabitRemoveArgs, None]
):
    """The command for removing a habit."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: HabitRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await HabitRemoveService().remove(
            context.domain_context, uow, progress_reporter, args.ref_id
        )
