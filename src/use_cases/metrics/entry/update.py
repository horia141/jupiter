"""The command for updating a metric entry's properties."""
from dataclasses import dataclass
from typing import Final, Optional

from domain.metrics.infra.metric_engine import MetricEngine
from domain.metrics.infra.metric_notion_manager import MetricNotionManager
from domain.adate import ADate
from models.framework import Command, UpdateAction, EntityId
from utils.time_provider import TimeProvider


class MetricEntryUpdateCommand(Command['MetricEntryUpdateCommand.Args', None]):
    """The command for updating a metric entry's properties."""

    @dataclass()
    class Args:
        """Args."""
        ref_id: EntityId
        collection_time: UpdateAction[ADate]
        value: UpdateAction[float]
        notes: UpdateAction[Optional[str]]

    _time_provider: Final[TimeProvider]
    _metric_engine: Final[MetricEngine]
    _notion_manager: Final[MetricNotionManager]

    def __init__(
            self, time_provider: TimeProvider, metric_engine: MetricEngine,
            notion_manager: MetricNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._metric_engine = metric_engine
        self._notion_manager = notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        with self._metric_engine.get_unit_of_work() as uow:
            metric_entry = uow.metric_entry_repository.load_by_id(args.ref_id)

            if args.collection_time.should_change:
                metric_entry.change_collection_time(args.collection_time.value, self._time_provider.get_current_time())
            if args.value.should_change:
                metric_entry.change_value(args.value.value, self._time_provider.get_current_time())
            if args.notes.should_change:
                metric_entry.change_notes(args.notes.value, self._time_provider.get_current_time())

            uow.metric_entry_repository.save(metric_entry)

        self._notion_manager.upsert_metric_entry(metric_entry)
