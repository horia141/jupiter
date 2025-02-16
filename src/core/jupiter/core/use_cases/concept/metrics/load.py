"""Use case for loading a metric."""

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_collection import (
    InboxTaskCollection,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.metrics.metric import Metric
from jupiter.core.domain.concept.metrics.metric_entry import MetricEntry
from jupiter.core.domain.core.notes.note import Note, NoteRepository
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class MetricLoadArgs(UseCaseArgsBase):
    """MetricLoadArgs."""

    ref_id: EntityId
    allow_archived: bool
    allow_archived_entries: bool


@use_case_result
class MetricLoadResult(UseCaseResultBase):
    """MetricLoadResult."""

    metric: Metric
    note: Note | None
    metric_entries: list[MetricEntry]
    metric_collection_inbox_tasks: list[InboxTask]


@readonly_use_case(WorkspaceFeature.METRICS)
class MetricLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MetricLoadArgs, MetricLoadResult]
):
    """Use case for loading a metric."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: MetricLoadArgs,
    ) -> MetricLoadResult:
        """Execute the command's action."""
        metric = await uow.get_for(Metric).load_by_id(
            args.ref_id, allow_archived=args.allow_archived
        )
        metric_entries = await uow.get_for(MetricEntry).find_all(
            metric.ref_id, allow_archived=args.allow_archived_entries
        )

        inbox_task_collection = await uow.get_for(InboxTaskCollection).load_by_parent(
            context.workspace.ref_id
        )
        metric_collection_inbox_tasks = await uow.get(
            InboxTaskRepository
        ).find_all_for_source_created_desc(
            parent_ref_id=inbox_task_collection.ref_id,
            allow_archived=True,
            source=InboxTaskSource.METRIC,
            source_entity_ref_id=metric.ref_id,
        )

        note = await uow.get(NoteRepository).load_optional_for_source(
            NoteDomain.METRIC,
            metric.ref_id,
            allow_archived=args.allow_archived,
        )

        return MetricLoadResult(
            metric=metric,
            note=note,
            metric_entries=metric_entries,
            metric_collection_inbox_tasks=metric_collection_inbox_tasks,
        )
