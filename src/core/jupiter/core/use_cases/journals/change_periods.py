"""Use case for changing the periods for journals."""
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
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
class JournalChangePeriodsArgs(UseCaseArgsBase):
    """Args."""

    periods: list[RecurringTaskPeriod]


@mutation_use_case(WorkspaceFeature.JOURNALS)
class JournalChangePeriodsUseCase(
    AppTransactionalLoggedInMutationUseCase[JournalChangePeriodsArgs, None]
):
    """THe use case for changing periods for journals."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: JournalChangePeriodsArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        journal_collection = await uow.journal_collection_repository.load_by_parent(
            workspace.ref_id
        )
        journal_collection = journal_collection.change_periods(
            context.domain_context, set(args.periods)
        )
        await uow.journal_collection_repository.save(journal_collection)