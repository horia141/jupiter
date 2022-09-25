"""The command for removing a metric entry."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.metrics.infra.metric_notion_manager import (
    MetricNotionManager,
    NotionMetricEntryNotFoundError,
)
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
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


class MetricEntryRemoveUseCase(
    AppMutationUseCase["MetricEntryRemoveUseCase.Args", None]
):
    """The command for removing a metric entry."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        ref_id: EntityId

    _metric_notion_manager: Final[MetricNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        metric_notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._metric_notion_manager = metric_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        with progress_reporter.start_removing_entity(
            "metric entry", args.ref_id
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                metric_entry = uow.metric_entry_repository.remove(args.ref_id)
                entity_reporter.mark_known_name(str(metric_entry.simple_name))
                metric = uow.metric_repository.load_by_id(metric_entry.metric_ref_id)
                entity_reporter.mark_local_change()

            try:
                self._metric_notion_manager.remove_leaf(
                    metric.metric_collection_ref_id, metric.ref_id, metric_entry.ref_id
                )
                entity_reporter.mark_remote_change()
            except NotionMetricEntryNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because metric was not found"
                )
                entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
