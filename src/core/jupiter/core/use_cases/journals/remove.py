"""Use case for removing a journal."""
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.infra.generic_remover import generic_remover
from jupiter.core.domain.journals.journal import Journal
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class JournalremoveArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.JOURNALS)
class JournalRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[JournalremoveArgs, None]
):
    """Use case for removing a journal."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: JournalremoveArgs,
    ) -> None:
        """Execute the command's action."""
        await generic_remover(
            context.domain_context, uow, progress_reporter, Journal, args.ref_id
        )
