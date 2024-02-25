"""The command for removing a metric entry."""

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_remove_service import NoteRemoveService
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric_entry import MetricEntry
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
class MetricEntryRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricEntryRemoveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricEntryRemoveArgs, None]
):
    """The command for removing a metric entry."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricEntryRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        metric_entry = await uow.get_for(MetricEntry).remove(args.ref_id)
        await progress_reporter.mark_removed(metric_entry)
        note_remove_service = NoteRemoveService()
        await note_remove_service.remove_for_source(
            context.domain_context, uow, NoteDomain.METRIC_ENTRY, metric_entry.ref_id
        )
