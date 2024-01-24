"""Use case for updating a journal entry."""
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.report.service.report_service import ReportService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInMutationUseCaseContext,
    mutation_use_case,
)


@use_case_args
class JournalUpdateReportArgs(UseCaseArgsBase):
    """Args."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.JOURNALS)
class JournalUpdateReportUseCase(
    AppLoggedInMutationUseCase[JournalUpdateReportArgs, None]
):
    """Use case for updating a journal entry."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: JournalUpdateReportArgs,
    ) -> None:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            journal = await uow.journal_repository.load_by_id(args.ref_id)

        report_service = ReportService(self._domain_storage_engine)

        report_period_result = await report_service.do_it(
            user=context.user,
            workspace=context.workspace,
            today=journal.right_now,
            period=journal.period,
        )

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            journal = journal.update_report(
                context.domain_context, report_period_result
            )
            await uow.journal_repository.save(journal)
            await progress_reporter.mark_updated(journal)
