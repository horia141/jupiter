"""The command for archiving a metric."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.metrics.infra.metric_notion_manager import (
    MetricNotionManager,
    NotionMetricNotFoundError,
    NotionMetricEntryNotFoundError,
)
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
    MarkProgressStatus,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricArchiveUseCase(AppMutationUseCase["MetricArchiveUseCase.Args", None]):
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
        metric_notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._metric_notion_manager = metric_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )

            metric = uow.metric_repository.load_by_key(
                metric_collection.ref_id, args.key
            )
            metric_entries_to_archive = uow.metric_entry_repository.find_all(
                parent_ref_id=metric.ref_id
            )
            inbox_tasks_to_archive = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                filter_sources=[InboxTaskSource.METRIC],
                filter_metric_ref_ids=[metric.ref_id],
            )

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
        )
        for inbox_task in inbox_tasks_to_archive:
            inbox_task_archive_service.do_it(progress_reporter, inbox_task)

        for metric_entry in metric_entries_to_archive:
            with progress_reporter.start_archiving_entity(
                "metric entry", metric_entry.ref_id, str(metric_entry.simple_name)
            ) as entity_reporter:
                with self._storage_engine.get_unit_of_work() as uow:
                    metric_entry = metric_entry.mark_archived(
                        EventSource.CLI, self._time_provider.get_current_time()
                    )
                    uow.metric_entry_repository.save(metric_entry)
                    entity_reporter.mark_local_change()

                try:
                    self._metric_notion_manager.remove_leaf(
                        metric_collection.ref_id, metric.ref_id, metric_entry.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionMetricEntryNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because metric entry was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

        with progress_reporter.start_archiving_entity(
            "metric", metric.ref_id, str(metric.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                metric = metric.mark_archived(
                    EventSource.CLI, self._time_provider.get_current_time()
                )
                uow.metric_repository.save(metric)

            try:
                self._metric_notion_manager.remove_branch(
                    metric_collection.ref_id, metric.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionMetricNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because metric was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
