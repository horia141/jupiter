"""The command for finding metrics."""
from dataclasses import dataclass
from typing import Final, Optional, List, Dict

from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.infra.metric_repository import MetricRepository
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from models.basic import MetricKey, EntityId
from models.framework import Command
from utils.time_provider import TimeProvider


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
        metric_entries: List[MetricEntry]

    @dataclass()
    class Response:
        """Response object."""

        metrics: List['MetricFindCommand.ResponseEntry']

    _time_provider: Final[TimeProvider]
    _metric_repository: Final[MetricRepository]
    _metric_entry_repository: Final[MetricEntryRepository]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, metric_repository: MetricRepository,
            metric_entry_repository: MetricEntryRepository, notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_repository = metric_repository
        self._metric_entry_repository = metric_entry_repository
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> 'Response':
        """Execute the command's action."""
        metrics = self._metric_repository.find_all(
            allow_archived=args.allow_archived, filter_keys=args.filter_keys)
        metric_entries = self._metric_entry_repository.find_all(
            allow_archived=args.allow_archived, filter_metric_ref_ids=[m.ref_id for m in metrics])
        metric_entries_by_ref_ids: Dict[EntityId, List[MetricEntry]] = {}
        for metric_entry in metric_entries:
            if metric_entry.metric_ref_id not in metric_entries_by_ref_ids:
                metric_entries_by_ref_ids[metric_entry.metric_ref_id] = [metric_entry]
            else:
                metric_entries_by_ref_ids[metric_entry.metric_ref_id].append(metric_entry)
        return self.Response(
            metrics=[self.ResponseEntry(
                metric=m,
                metric_entries=metric_entries_by_ref_ids.get(m.ref_id, [])) for m in metrics])
