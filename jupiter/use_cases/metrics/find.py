"""The command for finding metrics."""
import logging
import typing
from collections import defaultdict
from dataclasses import dataclass
from typing import Final, Optional, List, Dict, DefaultDict

from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.projects.project import Project
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase

LOGGER = logging.getLogger(__name__)


class MetricFindUseCase(UseCase['MetricFindUseCase.Args', 'MetricFindUseCase.Response']):
    """The command for finding metrics."""

    @dataclass()
    class Args:
        """Args."""
        allow_archived: bool
        filter_keys: Optional[List[MetricKey]]

    @dataclass()
    class ResponseEntry:
        """A single entry in the LoadAllMetricsResponse."""

        metric: Metric
        collection_project: Optional[Project]
        metric_entries: List[MetricEntry]
        metric_collection_inbox_tasks: Optional[List[InboxTask]]

    @dataclass()
    class Response:
        """Response object."""

        metrics: List['MetricFindUseCase.ResponseEntry']

    _storage_engine: Final[DomainStorageEngine]

    def __init__(self, storage_engine: DomainStorageEngine) -> None:
        """Constructor."""
        self._storage_engine = storage_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metrics = uow.metric_repository.find_all(
                allow_archived=args.allow_archived, filter_keys=args.filter_keys)
            metric_entries = uow.metric_entry_repository.find_all(
                allow_archived=args.allow_archived, filter_metric_ref_ids=[m.ref_id for m in metrics])
            metric_entries_by_ref_ids: Dict[EntityId, List[MetricEntry]] = {}
            projects_by_ref_id: Dict[EntityId, Project] = {}

            for metric in metrics:
                if metric.collection_params is None:
                    continue
                projects_by_ref_id[metric.ref_id] = \
                    uow.project_repository.load_by_id(metric.collection_params.project_ref_id)

            for metric_entry in metric_entries:
                if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)

            metric_collection_inbox_tasks_by_ref_id: DefaultDict[EntityId, List[InboxTask]] = defaultdict(list)
            all_inbox_tasks = \
                uow.inbox_task_repository.find_all(filter_metric_ref_ids=[m.ref_id for m in metrics])

            for inbox_task in all_inbox_tasks:
                metric_collection_inbox_tasks_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)]\
                    .append(inbox_task)

        return self.Response(
            metrics=[
                self.ResponseEntry(
                    metric=m,
                    collection_project=projects_by_ref_id.get(m.ref_id, None),
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, []),
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(m.ref_id, None))
                for m in metrics])
