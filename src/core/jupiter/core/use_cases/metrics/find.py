"""The command for finding metrics."""
import itertools
import typing
from collections import defaultdict
from typing import cast

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
    use_case_result_part,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class MetricFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_notes: bool
    include_entries: bool
    include_collection_inbox_tasks: bool
    include_metric_entry_notes: bool
    filter_ref_ids: list[EntityId] | None
    filter_entry_ref_ids: list[EntityId] | None


@use_case_result_part
class MetricFindResponseEntry(UseCaseResultBase):
    """A single entry in the LoadAllMetricsResponse."""

    metric: Metric
    note: Note | None
    metric_entries: list[MetricEntry] | None
    metric_collection_inbox_tasks: list[InboxTask] | None
    metric_entry_notes: list[Note] | None


@use_case_result
class MetricFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    collection_project: Project
    entries: list[MetricFindResponseEntry]


@readonly_use_case(WorkspaceFeature.METRICS)
class MetricFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MetricFindArgs, MetricFindResult]
):
    """The command for finding metrics."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: MetricFindArgs,
    ) -> MetricFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.get_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        metrics = await uow.get_for(Metric).find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        collection_project = await uow.get_for(Project).load_by_id(
            metric_collection.collection_project_ref_id,
        )

        all_notes_by_metric_ref_id: defaultdict[EntityId, Note] = defaultdict(None)
        if args.include_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            all_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.METRIC,
                allow_archived=True,
                source_entity_ref_id=[m.ref_id for m in metrics],
            )
            for n in all_notes:
                all_notes_by_metric_ref_id[n.source_entity_ref_id] = n

        if args.include_entries:
            metric_entries_raw = []
            for metric in metrics:
                metric_entries_raw.append(
                    await uow.get_for(MetricEntry).find_all(
                        parent_ref_id=metric.ref_id,
                        allow_archived=args.allow_archived,
                        filter_ref_ids=args.filter_entry_ref_ids,
                    ),
                )
            metric_entries = itertools.chain(*metric_entries_raw)

            metric_entries_by_ref_ids: dict[EntityId, list[MetricEntry]] = {}

            for metric_entry in metric_entries:
                if metric_entry.metric.ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric.ref_id] = [
                        metric_entry,
                    ]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric.ref_id].append(
                        metric_entry,
                    )
        else:
            metric_entries_by_ref_ids = {}

        if args.include_collection_inbox_tasks:
            metric_collection_inbox_tasks_by_ref_id: defaultdict[
                EntityId,
                list[InboxTask],
            ] = defaultdict(list)
            inbox_task_collection = await uow.get_for(
                InboxTaskCollection
            ).load_by_parent(
                workspace.ref_id,
            )
            all_inbox_tasks = await uow.get_for(InboxTask).find_all_generic(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                source=[InboxTaskSource.METRIC],
                metric_ref_id=[m.ref_id for m in metrics],
            )

            for inbox_task in all_inbox_tasks:
                metric_collection_inbox_tasks_by_ref_id[
                    typing.cast(EntityId, inbox_task.metric_ref_id)
                ].append(inbox_task)
        else:
            metric_collection_inbox_tasks_by_ref_id = defaultdict(list)

        all_notes_by_metric_entry_ref_id: defaultdict[EntityId, Note] = defaultdict(
            None
        )
        if args.include_metric_entry_notes:
            note_collection = await uow.get_for(NoteCollection).load_by_parent(
                workspace.ref_id
            )
            all_notes = await uow.get_for(Note).find_all_generic(
                parent_ref_id=note_collection.ref_id,
                domain=NoteDomain.METRIC_ENTRY,
                allow_archived=True,
                source_entity_ref_id=[me.ref_id for me in metric_entries],
            )
            for n in all_notes:
                all_notes_by_metric_entry_ref_id[
                    cast(EntityId, n.source_entity_ref_id)
                ] = n

        return MetricFindResult(
            collection_project=collection_project,
            entries=[
                MetricFindResponseEntry(
                    metric=m,
                    note=all_notes_by_metric_ref_id.get(m.ref_id, None),
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, [])
                    if len(metric_entries_by_ref_ids) > 0
                    else None,
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(
                        m.ref_id,
                        [],
                    )
                    if len(metric_collection_inbox_tasks_by_ref_id) > 0
                    else None,
                    metric_entry_notes=[
                        all_notes_by_metric_entry_ref_id[me.ref_id]
                        for me in metric_entries_by_ref_ids.get(m.ref_id, [])
                        if (me.ref_id in all_notes_by_metric_entry_ref_id)
                    ],
                )
                for m in metrics
            ],
        )
