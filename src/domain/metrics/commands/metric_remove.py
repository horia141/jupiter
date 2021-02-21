"""The command for hard removing a metric."""
import logging
from typing import Final

from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.infra.metric_repository import MetricRepository
from models.basic import MetricKey
from models.framework import Command
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class MetricRemoveCommand(Command[MetricKey, None]):
    """The command for removing a metric."""

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

    def execute(self, args: MetricKey) -> None:
        """Execute the command's action."""
        metric = self._metric_repository.get_by_key(args)

        for metric_entry in self._metric_entry_repository.find_all_for_metric(metric.ref_id):
            self._metric_entry_repository.remove(metric_entry)

        self._metric_repository.remove(metric)

        try:
            self._notion_manager.remove_metric(metric)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
