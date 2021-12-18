"""The command for archiving a metric entry."""
import logging
from typing import Final

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from models.framework import Command, EntityId
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class MetricEntryArchiveCommand(Command[EntityId, None]):
    """The command for archiving a metric entry."""

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, metric_engune: MetricEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engune
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.load_by_id(args)
            metric_entry.mark_archived(self._time_provider.get_current_time())
            uow.metric_entry_repository.save(metric_entry)

        try:
            self._notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
