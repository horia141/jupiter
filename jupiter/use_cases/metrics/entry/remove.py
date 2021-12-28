"""The command for removing a metric entry."""
import logging
from typing import Final

from jupiter.domain.metrics.infra.metric_engine import MetricEngine
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricEntryNotFoundError
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.use_case import UseCase

LOGGER = logging.getLogger(__name__)


class MetricEntryRemoveUseCase(UseCase[EntityId, None]):
    """The command for removing a metric entry."""

    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, metric_engune: MetricEngine, notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._metric_engine = metric_engune
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.remove(args)

        try:
            self._notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
        except NotionMetricEntryNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
