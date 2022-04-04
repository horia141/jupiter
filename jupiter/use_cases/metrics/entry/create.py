"""The command for creating a metric entry."""
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.notion_metric_entry import NotionMetricEntry
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider


class MetricEntryCreateUseCase(
    AppMutationUseCase["MetricEntryCreateUseCase.Args", None]
):
    """The command for creating a metric entry."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        metric_key: MetricKey
        collection_time: Optional[ADate]
        value: float
        notes: Optional[str]

    _notion_manager: Final[MetricNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        notion_manager: MetricNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._notion_manager = notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            metric = uow.metric_repository.load_by_key(
                metric_collection.ref_id, args.metric_key
            )
            collection_time = (
                args.collection_time
                if args.collection_time
                else ADate.from_timestamp(self._time_provider.get_current_time())
            )
            metric_entry = MetricEntry.new_metric_entry(
                archived=False,
                metric_ref_id=metric.ref_id,
                collection_time=collection_time,
                value=args.value,
                notes=args.notes,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time(),
            )
            metric_entry = uow.metric_entry_repository.create(metric_entry)
        notion_metric_entry = NotionMetricEntry.new_notion_entity(metric_entry, None)
        self._notion_manager.upsert_leaf(
            metric_collection.ref_id, metric.ref_id, notion_metric_entry, None
        )
