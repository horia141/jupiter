"""The command for archiving a vacation."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_archiver import generic_archiver
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class VacationArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.VACATIONS)
class VacationArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[VacationArchiveArgs, None]
):
    """The command for archiving a vacation."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: VacationArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_archiver(
            context.domain_context, uow, progress_reporter, Vacation, args.ref_id
        )
