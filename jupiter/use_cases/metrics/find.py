"""The command for finding metrics."""
import itertools
import logging
import typing
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict, DefaultDict

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.projects.project import Project
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCaseArgsBase, UseCaseResultBase
from jupiter.use_cases.infra.use_cases import AppReadonlyUseCase, AppUseCaseContext

LOGGER = logging.getLogger(__name__)


class MetricFindUseCase(AppReadonlyUseCase['MetricFindUseCase.Args', 'MetricFindUseCase.Result']):
    """The command for finding metrics."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        allow_archived: bool
        filter_keys: Optional[List[MetricKey]]

    @dataclass(frozen=True)
    class ResponseEntry:
        """A single entry in the LoadAllMetricsResponse."""

        metric: Metric
        metric_entries: List[MetricEntry]
        metric_collection_inbox_tasks: Optional[List[InboxTask]]

    @dataclass(frozen=True)
    class Result(UseCaseResultBase):
        """Result object."""

        collection_project: Project
        metrics: List['MetricFindUseCase.ResponseEntry']

    def _execute(self, context: AppUseCaseContext, args: Args) -> 'Result':
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_parent(workspace.ref_id)
            metrics = \
                uow.metric_repository.find_all(
                    parent_ref_id=metric_collection.ref_id,
                    allow_archived=args.allow_archived,
                    filter_keys=args.filter_keys)
            metric_entries = \
                itertools.chain(*(uow.metric_entry_repository.find_all(
                    parent_ref_id=m.ref_id, allow_archived=args.allow_archived) for m in metrics))
            metric_entries_by_ref_ids: Dict[EntityId, List[MetricEntry]] = {}

            collection_project = uow.project_repository.load_by_id(metric_collection.collection_project_ref_id)

            for metric_entry in metric_entries:
                if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)

            metric_collection_inbox_tasks_by_ref_id: DefaultDict[EntityId, List[InboxTask]] = defaultdict(list)
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(workspace.ref_id)
            all_inbox_tasks = \
                uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    filter_sources=[InboxTaskSource.METRIC],
                    filter_metric_ref_ids=[m.ref_id for m in metrics])

            for inbox_task in all_inbox_tasks:
                metric_collection_inbox_tasks_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)]\
                    .append(inbox_task)

        return self.Result(
            collection_project=collection_project,
            metrics=[
                self.ResponseEntry(
                    metric=m,
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, []),
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(m.ref_id, None))
                for m in metrics])
