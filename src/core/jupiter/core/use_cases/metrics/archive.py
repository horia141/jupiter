"""The command for archiving a metric."""

from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.notes.service.note_archive_service import (
    NoteArchiveService,
)
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.service.archive_service import (
    InboxTaskArchiveService,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.metrics.metric import Metric
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
class MetricArchiveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


@mutation_use_case(WorkspaceFeature.METRICS)
class MetricArchiveUseCase(
    AppTransactionalLoggedInMutationUseCase[MetricArchiveArgs, None]
):
    """The command for archiving a metric."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: MetricArchiveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        inbox_task_collection = (
            await uow.repository_for(InboxTaskCollection).load_by_parent(
                workspace.ref_id,
            )
        )

        metric = await uow.repository_for(Metric).load_by_id(args.ref_id)
        metric_entries_to_archive = await uow.repository_for(MetricEntry).find_all(
            parent_ref_id=metric.ref_id,
        )
        inbox_tasks_to_archive = await uow.repository_for(InboxTask).find_all_with_filters(
            parent_ref_id=inbox_task_collection.ref_id,
            filter_sources=[InboxTaskSource.METRIC],
            filter_metric_ref_ids=[metric.ref_id],
        )

        inbox_task_archive_service = InboxTaskArchiveService()
        for inbox_task in inbox_tasks_to_archive:
            await inbox_task_archive_service.do_it(
                context.domain_context, uow, progress_reporter, inbox_task
            )

        for metric_entry in metric_entries_to_archive:
            metric_entry = metric_entry.mark_archived(context.domain_context)
            await uow.repository_for(MetricEntry).save(metric_entry)
            await progress_reporter.mark_updated(metric_entry)

            note_archive_service = NoteArchiveService()
            await note_archive_service.archive_for_source(
                context.domain_context,
                uow,
                NoteDomain.METRIC_ENTRY,
                metric_entry.ref_id,
            )

        metric = metric.mark_archived(context.domain_context)
        await uow.repository_for(Metric).save(metric)
        await progress_reporter.mark_updated(metric)
