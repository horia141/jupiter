"""The command for creating a metric."""
from dataclasses import dataclass
from typing import Optional, Final

from domain.metrics.metric import Metric
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.infra.metric_repository import MetricRepository
from models.basic import MetricKey, RecurringTaskPeriod, MetricUnit, EntityName
from models.framework import Command
from utils.time_provider import TimeProvider


class MetricCreateCommand(Command['MetricCreateCommand.Args', None]):
    """The command for creating a metric."""

    @dataclass()
    class Args:
        """Args."""
        key: MetricKey
        name: EntityName
        collection_period: Optional[RecurringTaskPeriod]
        metric_unit: Optional[MetricUnit]

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
        metric = Metric.new_metric(
            args.key, args.name, args.collection_period, args.metric_unit, self._time_provider.get_current_time())
        metric = self._metric_repository.create(metric)
        self._notion_manager.upsert_metric(metric)
