"""The command for finding metrics."""
import logging
import typing
from collections import defaultdict
from dataclasses import dataclass
from typing import Final, Optional, List, Dict, DefaultDict

from domain.inbox_tasks.inbox_task import InboxTask
from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.metrics.metric_key import MetricKey
from domain.projects.infra.project_engine import ProjectEngine
from domain.projects.project import Project
from framework.entity_id import EntityId
from framework.use_case import UseCase

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

    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _metric_engine: Final[MetricEngine]

    def __init__(
            self, project_engine: ProjectEngine, inbox_task_engine: InboxTaskEngine,
            metric_engine: MetricEngine) -> None:
        """Constructor."""
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._metric_engine = metric_engine

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metrics = uow.metric_repository.find_all(
                allow_archived=args.allow_archived, filter_keys=args.filter_keys)
            metric_entries = uow.metric_entry_repository.find_all(
                allow_archived=args.allow_archived, filter_metric_ref_ids=[m.ref_id for m in metrics])
            metric_entries_by_ref_ids: Dict[EntityId, List[MetricEntry]] = {}
            projects_by_ref_id: Dict[EntityId, Project] = {}
            for metric in metrics:
                if metric.collection_params is None:
                    continue
                with self._project_engine.get_unit_of_work() as project_uow:
                    projects_by_ref_id[metric.ref_id] = \
                        project_uow.project_repository.load_by_id(metric.collection_params.project_ref_id)
            for metric_entry in metric_entries:
                if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)
        metric_collection_inbox_tasks_by_ref_id: DefaultDict[EntityId, List[InboxTask]] = defaultdict(list)
        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            all_inbox_tasks = \
                inbox_task_uow.inbox_task_repository.find_all(filter_metric_ref_ids=[m.ref_id for m in metrics])
        for inbox_task in all_inbox_tasks:
            metric_collection_inbox_tasks_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)].append(inbox_task)

        return self.Response(
            metrics=[
                self.ResponseEntry(
                    metric=m,
                    collection_project=projects_by_ref_id.get(m.ref_id, None),
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, []),
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(m.ref_id, None))
                for m in metrics])
