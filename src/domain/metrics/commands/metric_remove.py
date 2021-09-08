"""The command for hard removing a metric."""
import logging
from typing import Final

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.metrics.metric_key import MetricKey
from models.framework import Command
from remote.notion.common import CollectionEntityNotFound
from service.inbox_tasks import InboxTasksService
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class MetricRemoveCommand(Command[MetricKey, None]):
    """The command for removing a metric."""

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]
    _inbox_tasks_service: Final[InboxTasksService]

    def __init__(
            self, time_provider: TimeProvider, metric_engine: MetricEngine,
            notion_manager: MetricNotionManager, inbox_tasks_service: InboxTasksService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager
        self._inbox_tasks_service = inbox_tasks_service

    def execute(self, args: MetricKey) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.get_by_key(args)

            for metric_entry in uow.metric_entry_repository.find_all_for_metric(metric.ref_id, allow_archived=True):
                uow.metric_entry_repository.remove(metric_entry.ref_id)

            for metric_inbox_task in self._inbox_tasks_service.load_all_inbox_tasks(
                    filter_metric_ref_ids=[metric.ref_id]):
                self._inbox_tasks_service.hard_remove_inbox_task(metric_inbox_task.ref_id)

            uow.metric_repository.remove(metric.ref_id)

        try:
            self._notion_manager.remove_metric(metric)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
