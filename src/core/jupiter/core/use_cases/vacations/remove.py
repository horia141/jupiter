"""The command for removing a vacation entry."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_crown_remover import generic_crown_remover
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
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
class VacationRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.VACATIONS)
class VacationRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[VacationRemoveArgs, None]
):
    """The command for removing a vacation."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: VacationRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_crown_remover(
            context.domain_context, uow, progress_reporter, Vacation, args.ref_id
        )
