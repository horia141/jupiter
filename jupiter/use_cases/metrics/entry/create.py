"""The command for creating a metric entry."""
from dataclasses import dataclass
from typing import Optional, Final

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.notion_metric_entry import NotionMetricEntry
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class MetricEntryCreateUseCase(UseCase['MetricEntryCreateUseCase.Args', None]):
    """The command for creating a metric entry."""

    @dataclass()
    class Args:
        """Args."""
        metric_key: MetricKey
        collection_time: Optional[ADate]
        value: float
        notes: Optional[str]

    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, storage_engine: StorageEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._storage_engine.get_unit_of_work() as uow:
            metric = uow.metric_repository.load_by_key(args.metric_key)
            collection_time = args.collection_time \
                if args.collection_time else ADate.from_timestamp(self._time_provider.get_current_time())
            metric_entry = MetricEntry.new_metric_entry(
                False, metric.ref_id, collection_time, args.value, args.notes,
                self._time_provider.get_current_time())
            metric_entry = uow.metric_entry_repository.create(metric_entry)
        notion_metric_entry = NotionMetricEntry.new_notion_row(metric_entry, None)
        self._notion_manager.upsert_metric_entry(metric.ref_id, notion_metric_entry)
