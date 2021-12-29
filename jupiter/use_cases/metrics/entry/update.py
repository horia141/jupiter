"""The command for updating a metric entry's properties."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.storage_engine import StorageEngine
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider


class MetricEntryUpdateUseCase(UseCase['MetricEntryUpdateUseCase.Args', None]):
    """The command for updating a metric entry's properties."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        collection_time: UpdateAction[ADate]
        value: UpdateAction[float]
        notes: UpdateAction[Optional[str]]

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
            metric_entry = uow.metric_entry_repository.load_by_id(args.ref_id)

            if args.collection_time.should_change:
                metric_entry.change_collection_time(args.collection_time.value, self._time_provider.get_current_time())
            if args.value.should_change:
                metric_entry.change_value(args.value.value, self._time_provider.get_current_time())
            if args.notes.should_change:
                metric_entry.change_notes(args.notes.value, self._time_provider.get_current_time())

            uow.metric_entry_repository.save(metric_entry)

        notion_metric_entry = self._notion_manager.load_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
        notion_metric_entry = notion_metric_entry.join_with_aggregate_root(metric_entry, None)
        self._notion_manager.save_metric_entry(metric_entry.metric_ref_id, notion_metric_entry)
