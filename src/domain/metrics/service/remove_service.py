"""Shared service for removing a metric."""
import logging
from typing import Final

from domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric import Metric
from remote.notion.common import CollectionEntityNotFound
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricRemoveService:
    """Shared service for removing a metric."""

    _time_provider: Final[TimeProvider]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_engine: Final[MetricEngine]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, inbox_task_engine: InboxTaskEngine,
            inbox_task_notion_manager: InboxTaskNotionManager, metric_engine: MetricEngine,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_engine = metric_engine
        self._metric_notion_manager = metric_notion_manager

    def execute(self, metric: Metric) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            for metric_entry in uow.metric_entry_repository.find_all_for_metric(metric.ref_id, allow_archived=True):
                uow.metric_entry_repository.remove(metric_entry.ref_id)

            uow.metric_repository.remove(metric.ref_id)

        with self._inbox_task_engine.get_unit_of_work() as inbox_task_uow:
            all_inbox_tasks = inbox_task_uow.inbox_task_repository.find_all(
                filter_metric_ref_ids=[metric.ref_id])

        inbox_task_remove_service = InboxTaskRemoveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_remove_service.do_it(inbox_task)

        # This needs to take into account notion entries too.
        try:
            self._metric_notion_manager.remove_metric(metric)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
