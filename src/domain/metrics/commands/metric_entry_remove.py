"""The command for removing a metric entry."""
import logging
from typing import Final

from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from models.basic import EntityId
from models.framework import Command
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class MetricEntryRemoveCommand(Command[EntityId, None]):
    """The command for removing a metric entry."""

    _time_provider: Final[TimeProvider]
    _metric_entry_repository: Final[MetricEntryRepository]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, metric_entry_repository: MetricEntryRepository,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_entry_repository = metric_entry_repository
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        metric_entry = self._metric_entry_repository.load_by_id(args)
        self._metric_entry_repository.remove(metric_entry)

        try:
            self._notion_manager.remove_metric_entry(metric_entry)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
