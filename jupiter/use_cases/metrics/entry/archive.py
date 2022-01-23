"""The command for archiving a metric entry."""
import logging
from typing import Final

from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricEntryNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricEntryArchiveUseCase(UseCase[EntityId, None]):
    """The command for archiving a metric entry."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[DomainStorageEngine]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: DomainStorageEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._notion_manager = notion_manager

    def execute(self, args: EntityId) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.load_by_id(args)
            metric_entry = metric_entry.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.metric_entry_repository.save(metric_entry)

        try:
            self._notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
        except NotionMetricEntryNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
