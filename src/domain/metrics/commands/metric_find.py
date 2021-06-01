"""The command for finding metrics."""
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Final, Optional, List, Dict, DefaultDict

import typing

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from models.basic import MetricKey
from models.framework import Command, EntityId
from service.inbox_tasks import InboxTask, InboxTasksService
from service.projects import Project, ProjectsService

LOGGER = logging.getLogger(__name__)


class MetricFindCommand(Command['MetricFindCommand.Args', 'MetricFindCommand.Response']):
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

        metrics: List['MetricFindCommand.ResponseEntry']

    _metric_engine: Final[MetricEngine]
    _project_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, metric_engine: MetricEngine, project_service: ProjectsService,
            inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._metric_engine = metric_engine
        self._project_service = project_service
        self._inbox_tasks_service = inbox_tasks_service

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
                projects_by_ref_id[metric.ref_id] = \
                    self._project_service.load_project_by_ref_id(metric.collection_params.project_ref_id)
            for metric_entry in metric_entries:
                if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
                else:
                    metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)
        metric_collection_inbox_tasks_by_ref_id: DefaultDict[EntityId, List[InboxTask]] = defaultdict(list)
        for inbox_task in self._inbox_tasks_service.load_all_inbox_tasks(
                filter_metric_ref_ids=[m.ref_id for m in metrics]):
            metric_collection_inbox_tasks_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)].append(inbox_task)

        return self.Response(
            metrics=[
                self.ResponseEntry(
                    metric=m,
                    collection_project=projects_by_ref_id.get(m.ref_id, None),
                    metric_entries=metric_entries_by_ref_ids.get(m.ref_id, []),
                    metric_collection_inbox_tasks=metric_collection_inbox_tasks_by_ref_id.get(m.ref_id, None))
                for m in metrics])
