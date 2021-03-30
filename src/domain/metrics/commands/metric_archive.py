"""The command for archiving a metric."""
import logging
from typing import Final

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from models.basic import MetricKey
from models.framework import Command
from remote.notion.common import CollectionEntityNotFound
from service.inbox_tasks import InboxTasksService
from utils.time_provider import TimeProvider


LOGGER = logging.getLogger(__name__)


class MetricArchiveCommand(Command[MetricKey, None]):
    """The command for archiving a metric."""

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

            for metric_entry in uow.metric_entry_repository.find_all_for_metric(metric.ref_id):
                metric_entry.mark_archived(archived_time=self._time_provider.get_current_time())
                uow.metric_entry_repository.save(metric_entry)

            for metric_inbox_task in self._inbox_tasks_service.load_all_inbox_tasks(
                    filter_metric_ref_ids=[metric.ref_id]):
                self._inbox_tasks_service.archive_inbox_task(metric_inbox_task.ref_id)

            metric.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.metric_repository.save(metric)

        try:
            self._notion_manager.remove_metric(metric)
        except CollectionEntityNotFound:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
