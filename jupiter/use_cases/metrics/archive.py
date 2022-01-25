"""The command for archiving a metric."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricNotFoundError
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, MutationUseCaseInvocationRecorder
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricArchiveUseCase(AppMutationUseCase['MetricArchiveUseCase.Args', None]):
    """The command for archiving a metric."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        key: MetricKey

    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            inbox_task_notion_manager: InboxTaskNotionManager,
            metric_notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.load_by_key(args.key)

            for metric_entry in uow.metric_entry_repository.find_all_for_metric(metric.ref_id):
                metric_entry = metric_entry.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
                uow.metric_entry_repository.save(metric_entry)

            metric = metric.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.metric_repository.save(metric)

            all_inbox_tasks = uow.inbox_task_repository.find_all(filter_metric_ref_ids=[metric.ref_id])

        inbox_task_archive_service = \
            InboxTaskArchiveService(
                source=EventSource.CLI, time_provider=self._time_provider, storage_engine=self._storage_engine,
                inbox_task_notion_manager=self._inbox_task_notion_manager)
        for inbox_task in all_inbox_tasks:
            inbox_task_archive_service.do_it(inbox_task)

        # TODO(horia141): process Notion side entries too
        try:
            self._metric_notion_manager.remove_metric(metric.ref_id)
        except NotionMetricNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
