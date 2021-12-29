"""The command for archiving a metric."""
import logging
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricNotFoundError
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricArchiveUseCase(UseCase[MetricKey, None]):
    """The command for archiving a metric."""

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def execute(self, args: MetricKey) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.load_by_key(args)

            for metric_entry in uow.metric_entry_repository.find_all_for_metric(metric.ref_id):
                metric_entry.mark_archived(archived_time=self._time_provider.get_current_time())
                uow.metric_entry_repository.save(metric_entry)

            metric.mark_archived(archived_time=self._time_provider.get_current_time())
            uow.metric_repository.save(metric)

            all_inbox_tasks = uow.inbox_task_repository.find_all(filter_metric_ref_ids=[metric.ref_id])

        inbox_task_archive_service = \
            InboxTaskArchiveService(self._time_provider, self._storage_engine, self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_archive_service.do_it(inbox_task)

        # TODO(horia141): process Notion side entries too
        try:
            self._metric_notion_manager.remove_metric(metric.ref_id)
        except NotionMetricNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
