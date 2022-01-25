"""The command for archiving a metric entry."""
import logging
from dataclasses import dataclass
from typing import Final

from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricEntryNotFoundError
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, MutationUseCaseInvocationRecorder
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class MetricEntryArchiveUseCase(AppMutationUseCase['MetricEntryArchiveUseCase.Args', None]):
    """The command for archiving a metric entry."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        ref_id: EntityId

    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._notion_manager = notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.load_by_id(args.ref_id)
            metric_entry = metric_entry.mark_archived(EventSource.CLI, self._time_provider.get_current_time())
            uow.metric_entry_repository.save(metric_entry)

        try:
            self._notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
        except NotionMetricEntryNotFoundError:
            LOGGER.info("Skipping archival on Notion side because metric was not found")
