"""The command for creating a metric entry."""
from dataclasses import dataclass
from typing import Optional, Final

from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.infra.metric_repository import MetricRepository
from domain.metrics.metric_entry import MetricEntry
from models.basic import MetricKey, ADate
from models.framework import Command
from utils.time_provider import TimeProvider


class MetricEntryCreateCommand(Command['MetricEntryCreateCommand.Args', None]):
    """The command for creating a metric entry."""

    @dataclass()
    class Args:
        """Args."""
        metric_key: MetricKey
        collection_time: Optional[ADate]
        value: float
        notes: Optional[str]

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

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        metric = self._metric_repository.get_by_key(args.metric_key)
        metric_entry = MetricEntry.new_metric_entry(
            metric.ref_id, args.collection_time, args.value, args.notes, self._time_provider.get_current_time())
        metric_entry = self._metric_entry_repository.create(metric_entry)
        self._notion_manager.upsert_metric_entry(metric_entry)
