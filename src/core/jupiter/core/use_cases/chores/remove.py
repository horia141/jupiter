"""The command for removing a chore."""
from dataclasses import dataclass

from jupiter.core.domain.chores.service.remove_service import ChoreRemoveService
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
class ChoreRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.CHORES)
class ChoreRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[ChoreRemoveArgs, None]
):
    """The command for removing a chore."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ChoreRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        await ChoreRemoveService().remove(
            context.domain_context, uow, progress_reporter, args.ref_id
        )
