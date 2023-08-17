"""The command for finding metrics."""
import itertools
import typing
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, List, Optional

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class MetricFindArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    allow_archived: bool
    include_entries: bool
    include_collection_inbox_tasks: bool
    filter_ref_ids: Optional[List[EntityId]] = None
    filter_entry_ref_ids: Optional[List[EntityId]] = None


@dataclass
class MetricFindResponseEntry:
    """A single entry in the LoadAllMetricsResponse."""

    metric: Metric
    metric_entries: Optional[List[MetricEntry]] = None
    metric_collection_inbox_tasks: Optional[List[InboxTask]] = None


@dataclass
class MetricFindResult(UseCaseResultBase):
    """PersonFindResult object."""

    collection_project: Project
    entries: List[MetricFindResponseEntry]


class MetricFindUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[MetricFindArgs, MetricFindResult]
):
    """The command for finding metrics."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: MetricFindArgs,
    ) -> MetricFindResult:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.metric_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        metrics = await uow.metric_repository.find_all(
            parent_ref_id=metric_collection.ref_id,
            allow_archived=args.allow_archived,
            filter_ref_ids=args.filter_ref_ids,
        )

        collection_project = await uow.project_repository.load_by_id(
            metric_collection.collection_project_ref_id,
        )

        if args.include_entries:
            metric_entries_raw = []
            for metric in metrics:
                metric_entries_raw.append(
                    await uow.metric_entry_repository.find_all(
                        parent_ref_id=metric.ref_id,
                        allow_archived=args.allow_archived,
                        filter_ref_ids=args.filter_entry_ref_ids,
                    ),
                )
            metric_entries = itertools.chain(*metric_entries_raw)

            metric_entries_by_ref_ids: Dict[EntityId, List[MetricEntry]] = {}

            for metric_entry in metric_entries:
                if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [
                        metric_entry,
                    ]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(
                        metric_entry,
                    )
        else:
            metric_entries_by_ref_ids = {}

        if args.include_collection_inbox_tasks:
            metric_collection_inbox_tasks_by_ref_id: DefaultDict[
                EntityId,
                List[InboxTask],
            ] = defaultdict(list)
            inbox_task_collection = (
                await uow.inbox_task_collection_repository.load_by_parent(
                    workspace.ref_id,
                )
            )
            all_inbox_tasks = await uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.METRIC],
                filter_metric_ref_ids=[m.ref_id for m in metrics],
            )

            for inbox_task in all_inbox_tasks:
                metric_collection_inbox_tasks_by_ref_id[
                    typing.cast(EntityId, inbox_task.metric_ref_id)
                ].append(inbox_task)
        else:
            metric_collection_inbox_tasks_by_ref_id = defaultdict(list)

        return MetricFindResult(
            collection_project=collection_project,
            entries=[
                MetricFindResponseEntry(
                    metric=m,
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, [])
                    if len(metric_entries_by_ref_ids) > 0
                    else None,
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(
                        m.ref_id,
                        [],
                    )
                    if len(metric_collection_inbox_tasks_by_ref_id) > 0
                    else None,
                )
                for m in metrics
            ],
        )
