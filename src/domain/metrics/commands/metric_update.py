"""The command for updating a metric's properties."""
from dataclasses import dataclass
from typing import Final, Optional

from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.infra.metric_repository import MetricRepository
from models.basic import MetricKey, RecurringTaskPeriod, EntityName
from models.framework import Command, UpdateAction
from utils.time_provider import TimeProvider


class MetricUpdateCommand(Command['MetricUpdateCommand.Args', None]):
    """The command for updating a metric's properties."""

    @dataclass()
    class Args:
        """Args."""
        key: MetricKey
        name: UpdateAction[EntityName]
        collection_period: UpdateAction[Optional[RecurringTaskPeriod]]

    _time_provider: Final[TimeProvider]
    _metric_repository: Final[MetricRepository]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, metric_repository: MetricRepository,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_repository = metric_repository
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        metric = self._metric_repository.get_by_key(args.key)

        if args.name.should_change:
            metric.change_name(args.name.value, self._time_provider.get_current_time())
        if args.collection_period.should_change:
            metric.change_collection_period(args.collection_period.value, self._time_provider.get_current_time())

        self._metric_repository.save(metric)
        self._notion_manager.upsert_metric(metric)
