"""Repository for metrics."""
import logging
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Iterable, ClassVar, Final
import typing

from models.basic import EntityId, MetricKey, RecurringTaskPeriod, MetricUnit, BasicValidator, ADate
from repository.common import RepositoryError
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, In, Eq
from utils.time_field_action import TimeFieldAction
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class MetricRow(BaseEntityRow):
    """A container for metric entries."""
    key: MetricKey
    name: str
    collection_period: Optional[RecurringTaskPeriod]
    metric_unit: Optional[MetricUnit]


class MetricsRepository:
    """A repository for metrics."""

    _METRICS_FILE_PATH: ClassVar[Path] = Path("./metrics.yaml")

    _storage: Final[EntitiesStorage[MetricRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[MetricRow](self._METRICS_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'MetricsRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_metric(
            self, key: MetricKey, name: str, archived: bool, collection_period: Optional[RecurringTaskPeriod],
            metric_unit: Optional[MetricUnit]) -> MetricRow:
        """Create a metric."""
        metric_rows = self._storage.find_all(allow_archived=True, key=Eq(key))

        if len(metric_rows) > 0:
            raise RepositoryError(f"Metric with key='{key}' already exists")

        new_metric_row = MetricRow(
            key=key, name=name, archived=archived, collection_period=collection_period, metric_unit=metric_unit)
        return self._storage.create(new_metric_row)

    def archive_metric(self, ref_id: EntityId) -> MetricRow:
        """Archive a metric."""
        return self._storage.archive(ref_id)

    def remove_metric(self, ref_id: EntityId) -> MetricRow:
        """Hard remove a metric."""
        return self._storage.remove(ref_id=ref_id)

    def update_metric(
            self, new_metric: MetricRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> MetricRow:
        """Store a particular metric."""
        return self._storage.update(new_metric, archived_time_action=archived_time_action)

    def load_metric(self, ref_id: EntityId, allow_archived: bool = False) -> MetricRow:
        """Load a particular metric by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def load_metric_by_key(self, key: MetricKey, allow_archived: bool = False) -> MetricRow:
        """Load a particular metric by its id."""
        return self._storage.find_first(allow_archived=allow_archived, key=Eq(key))

    def find_all_metrics(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> Iterable[MetricRow]:
        """Load all metrics."""
        return self._storage.find_all(
            allow_archived=allow_archived, ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            key=In(*filter_keys) if filter_keys else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "key": {"type": "string"},
            "collection_period": {"type": ["string", "null"]},
            "metric_unit": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> MetricRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return MetricRow(
            name=typing.cast(str, storage_form["name"]),
            key=MetricKey(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]),
            collection_period=RecurringTaskPeriod(typing.cast(str, storage_form["collection_period"]))
            if storage_form["collection_period"] else None,
            metric_unit=MetricUnit(typing.cast(str, storage_form["metric_unit"]))
            if storage_form["metric_unit"] else None)

    @staticmethod
    def live_to_storage(live_form: MetricRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "key": live_form.key,
            "collection_period": live_form.collection_period.value if live_form.collection_period else None,
            "metric_unit": live_form.metric_unit.value if live_form.metric_unit else None
        }


@dataclass()
class MetricEntryRow(BaseEntityRow):
    """An entry in a metric."""

    metric_ref_id: EntityId
    collection_time: ADate
    value: float
    notes: Optional[str]


class MetricEntriesRepository:
    """A repository for metric entries."""

    _METRIC_ENTRIES_FILE_PATH: ClassVar[Path] = Path("./metric-entries.yaml")

    _storage: Final[EntitiesStorage[MetricEntryRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[MetricEntryRow](
            self._METRIC_ENTRIES_FILE_PATH, time_provider, self)

    def __enter__(self) -> 'MetricEntriesRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def create_metric_entry(
            self, metric_ref_id: EntityId, collection_time: ADate, value: float, notes: Optional[str],
            archived: bool) -> MetricEntryRow:
        """Create a metric entry."""
        new_metric_entries = MetricEntryRow(
            metric_ref_id=metric_ref_id, collection_time=collection_time, value=value, notes=notes, archived=archived)
        return self._storage.create(new_metric_entries)

    def archive_metric_entry(self, ref_id: EntityId) -> MetricEntryRow:
        """Archive a metric entry."""
        return self._storage.archive(ref_id)

    def remove_metric_entry(self, ref_id: EntityId) -> MetricEntryRow:
        """Hard remove a metric entry."""
        return self._storage.remove(ref_id=ref_id)

    def update_metric_entry(
            self, new_metric_entries: MetricEntryRow,
            archived_time_action: TimeFieldAction = TimeFieldAction.DO_NOTHING) -> MetricEntryRow:
        """Store a particular metric entry."""
        return self._storage.update(new_metric_entries, archived_time_action=archived_time_action)

    def load_metric_entry(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntryRow:
        """Load a particular metric entry by its id."""
        return self._storage.load(ref_id, allow_archived=allow_archived)

    def find_all_metric_entries(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> Iterable[MetricEntryRow]:
        """Load all metrics entries."""
        return self._storage.find_all(
            allow_archived=allow_archived,
            ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
            metric_ref_id=In(*filter_metric_ref_ids) if filter_metric_ref_ids else None)

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "metric_ref_id": {"type": "string"},
            "name": {"type": "string"},
            "collection_time": {"type": "string"},
            "value": {"type": "number"},
            "notes": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> MetricEntryRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return MetricEntryRow(
            metric_ref_id=EntityId(typing.cast(str, storage_form["metric_ref_id"])),
            collection_time=BasicValidator.adate_from_str(typing.cast(str, storage_form["collection_time"])),
            value=typing.cast(float, storage_form["value"]),
            notes=typing.cast(str, storage_form["notes"]) if storage_form.get("notes", None) else None,
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: MetricEntryRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "metric_ref_id": live_form.metric_ref_id,
            "collection_time": BasicValidator.adate_to_str(live_form.collection_time),
            "value": live_form.value,
            "notes": live_form.notes
        }
