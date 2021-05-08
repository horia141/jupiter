"""YAML text files repository for metrics."""
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Optional, Iterable, ClassVar, Final
import typing

from domain.metrics.infra.metric_engine import MetricUnitOfWork, MetricEngine
from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.metric import Metric
from domain.shared import RecurringTaskGenParams
from domain.metrics.infra.metric_repository import MetricRepository
from domain.metrics.metric_entry import MetricEntry
from models.basic import EntityId, MetricKey, RecurringTaskPeriod, MetricUnit, BasicValidator, ADate, EntityName
from models.errors import RepositoryError
from utils.storage import JSONDictType, BaseEntityRow, EntitiesStorage, In, Eq
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


@dataclass()
class _MetricRow(BaseEntityRow):
    """A container for metric entries."""
    key: MetricKey
    name: EntityName
    collection_project_ref_id: Optional[EntityId]
    collection_period: Optional[RecurringTaskPeriod]
    collection_eisen: typing.List[str]
    collection_difficulty: Optional[str]
    collection_actionable_from_day: Optional[int]
    collection_actionable_from_month: Optional[int]
    collection_due_at_time: Optional[str]
    collection_due_at_day: Optional[int]
    collection_due_at_month: Optional[int]
    metric_unit: Optional[MetricUnit]


class YamlMetricRepository(MetricRepository):
    """A repository for metrics."""

    _METRICS_FILE_PATH: ClassVar[Path] = Path("./metrics")
    _METRICS_NUM_SHARDS: ClassVar[int] = 1

    _storage: Final[EntitiesStorage[_MetricRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_MetricRow](
            self._METRICS_FILE_PATH, self._METRICS_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlMetricRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, metric: Metric) -> Metric:
        """Create a metric."""
        metric_rows = self._storage.find_all(allow_archived=True, key=Eq(metric.key))

        if len(metric_rows) > 0:
            raise RepositoryError(f"Metric with key='{metric.key}' already exists")

        new_metric_row = self._storage.create(_MetricRow(
            key=metric.key,
            name=metric.name,
            archived=metric.archived,
            collection_project_ref_id=metric.collection_params.project_ref_id if metric.collection_params else None,
            collection_period=metric.collection_params.period if metric.collection_params else None,
            collection_eisen=[e.value for e in metric.collection_params.eisen] if metric.collection_params else [],
            collection_difficulty=metric.collection_params.difficulty.value
            if metric.collection_params and metric.collection_params.difficulty else None,
            collection_actionable_from_day=metric.collection_params.actionable_from_day
            if metric.collection_params else None,
            collection_actionable_from_month=metric.collection_params.actionable_from_month
            if metric.collection_params else None,
            collection_due_at_day=metric.collection_params.due_at_day if metric.collection_params else None,
            collection_due_at_month=metric.collection_params.actionable_from_month
            if metric.collection_params else None,
            collection_due_at_time=metric.collection_params.due_at_time if metric.collection_params else None,
            metric_unit=metric.metric_unit))
        metric.assign_ref_id(new_metric_row.ref_id)
        return metric

    def save(self, metric: Metric) -> Metric:
        """Save a metric - it should already exist."""
        metric_row = self._entity_to_row(metric)
        metric_row = self._storage.update(metric_row)
        return self._row_to_entity(metric_row)

    def get_by_key(self, key: MetricKey) -> Metric:
        """Retrieve a metric by its key."""
        metric_row = self._storage.find_first(allow_archived=False, key=Eq(key))
        return self._row_to_entity(metric_row)

    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
        """Load a particular metric by its id."""
        return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))

    def find_all(
            self, allow_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> typing.List[Metric]:
        """Find all metrics matching some criteria."""
        return [self._row_to_entity(mr)
                for mr in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
                    key=In(*filter_keys) if filter_keys else None)]

    def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric."""
        return self._row_to_entity(self._storage.remove(ref_id=ref_id))

    @staticmethod
    def storage_schema() -> JSONDictType:
        """The schema for the data."""
        return {
            "name": {"type": "string"},
            "key": {"type": "string"},
            "collection_project_ref_id": {"type": ["string", "null"]},
            "collection_period": {"type": ["string", "null"]},
            "collection_eisen": {
                "type": "array",
                "entries": {"type": "string"}
            },
            "collection_difficulty": {"type": ["string", "null"]},
            "collection_actionable_from_day": {"type": ["number", "null"]},
            "collection_actionable_from_month": {"type": ["number", "null"]},
            "collection_due_at_time": {"type": ["string", "null"]},
            "collection_due_at_day": {"type": ["number", "null"]},
            "collection_due_at_month": {"type": ["number", "null"]},
            "metric_unit": {"type": ["string", "null"]}
        }

    @staticmethod
    def storage_to_live(storage_form: JSONDictType) -> _MetricRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _MetricRow(
            name=EntityName(typing.cast(str, storage_form["name"])),
            key=MetricKey(typing.cast(str, storage_form["key"])),
            archived=typing.cast(bool, storage_form["archived"]),
            collection_project_ref_id=EntityId(typing.cast(str, storage_form["collection_project_ref_id"])),
            collection_period=RecurringTaskPeriod(typing.cast(str, storage_form["collection_period"]))
            if storage_form["collection_period"] else None,
            collection_eisen=typing.cast(typing.List[str], storage_form["collection_eisen"]),
            collection_difficulty=typing.cast(str, storage_form["collection_difficulty"])
            if storage_form["collection_difficulty"] else None,
            collection_actionable_from_day=typing.cast(int, storage_form["collection_actionable_from_day"])
            if storage_form.get("collection_actionable_from_day", None) else None,
            collection_actionable_from_month=typing.cast(int, storage_form["collection_actionable_from_month"])
            if storage_form.get("collection_actionable_from_month", None) else None,
            collection_due_at_time=typing.cast(str, storage_form["collection_due_at_time"])
            if storage_form["collection_due_at_time"] else None,
            collection_due_at_day=typing.cast(int, storage_form["collection_due_at_day"])
            if storage_form["collection_due_at_day"] else None,
            collection_due_at_month=typing.cast(int, storage_form["collection_due_at_month"])
            if storage_form["collection_due_at_month"] else None,
            metric_unit=MetricUnit(typing.cast(str, storage_form["metric_unit"]))
            if storage_form["metric_unit"] else None)

    @staticmethod
    def live_to_storage(live_form: _MetricRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "name": live_form.name,
            "key": live_form.key,
            "collection_project_ref_id": live_form.collection_project_ref_id,
            "collection_period": live_form.collection_period.value if live_form.collection_period else None,
            "collection_eisen": live_form.collection_eisen,
            "collection_difficulty": live_form.collection_difficulty,
            "collection_actionable_from_day": live_form.collection_actionable_from_day,
            "collection_actionable_from_month": live_form.collection_actionable_from_month,
            "collection_due_at_time": live_form.collection_due_at_time,
            "collection_due_at_day": live_form.collection_due_at_day,
            "collection_due_at_month": live_form.collection_due_at_month,
            "metric_unit": live_form.metric_unit.value if live_form.metric_unit else None
        }

    @staticmethod
    def _entity_to_row(metric: Metric) -> _MetricRow:
        metric_row = _MetricRow(
            archived=metric.archived,
            key=metric.key,
            name=metric.name,
            collection_project_ref_id=metric.collection_params.project_ref_id if metric.collection_params else None,
            collection_period=metric.collection_params.period if metric.collection_params else None,
            collection_eisen=[e.value for e in metric.collection_params.eisen] if metric.collection_params else [],
            collection_difficulty=metric.collection_params.difficulty.value
            if metric.collection_params and metric.collection_params.difficulty else None,
            collection_actionable_from_day=metric.collection_params.actionable_from_day
            if metric.collection_params else None,
            collection_actionable_from_month=metric.collection_params.actionable_from_month
            if metric.collection_params else None,
            collection_due_at_day=metric.collection_params.due_at_day if metric.collection_params else None,
            collection_due_at_month=metric.collection_params.actionable_from_month
            if metric.collection_params else None,
            collection_due_at_time=metric.collection_params.due_at_time if metric.collection_params else None,
            metric_unit=metric.metric_unit)
        metric_row.ref_id = metric.ref_id
        metric_row.created_time = metric.created_time
        metric_row.archived_time = metric.archived_time
        metric_row.last_modified_time = metric.last_modified_time
        return metric_row

    @staticmethod
    def _row_to_entity(row: _MetricRow) -> Metric:
        return Metric(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _key=row.key,
            _name=row.name,
            _collection_params=RecurringTaskGenParams(
                project_ref_id=row.collection_project_ref_id,
                period=row.collection_period,
                eisen=[BasicValidator.eisen_validate_and_clean(e) for e in row.collection_eisen],
                difficulty=BasicValidator.difficulty_validate_and_clean(row.collection_difficulty)
                if row.collection_difficulty else None,
                actionable_from_day=row.collection_actionable_from_day,
                actionable_from_month=row.collection_actionable_from_month,
                due_at_day=row.collection_due_at_day,
                due_at_month=row.collection_due_at_month,
                due_at_time=row.collection_due_at_time)
            if row.collection_project_ref_id is not None and row.collection_period is not None else None,
            _metric_unit=row.metric_unit)


@dataclass()
class _MetricEntryRow(BaseEntityRow):
    """An entry in a metric."""

    metric_ref_id: EntityId
    collection_time: ADate
    value: float
    notes: Optional[str]


class YamlMetricEntryRepository(MetricEntryRepository):
    """A repository for metric entries."""

    _METRIC_ENTRIES_FILE_PATH: ClassVar[Path] = Path("./metric-entries")
    _METRIC_ENTRIES_NUM_SHARDS: ClassVar[int] = 10

    _storage: Final[EntitiesStorage[_MetricEntryRow]]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._storage = EntitiesStorage[_MetricEntryRow](
            self._METRIC_ENTRIES_FILE_PATH, self._METRIC_ENTRIES_NUM_SHARDS, time_provider, self)

    def __enter__(self) -> 'YamlMetricEntryRepository':
        """Enter context."""
        self._storage.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def initialize(self) -> None:
        """Initialise the repo."""
        self._storage.initialize()

    def create(self, metric_entry: MetricEntry) -> MetricEntry:
        """Create a metric entry."""
        new_metric_entry_row = self._storage.create(_MetricEntryRow(
            archived=metric_entry.archived,
            metric_ref_id=metric_entry.metric_ref_id,
            collection_time=metric_entry.collection_time,
            value=metric_entry.value,
            notes=metric_entry.notes))
        metric_entry.assign_ref_id(new_metric_entry_row.ref_id)
        return metric_entry

    def save(self, metric_entry: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""
        metric_entry_row = self._entity_to_row(metric_entry)
        metric_entry_row = self._storage.update(metric_entry_row)
        return self._row_to_entity(metric_entry_row)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntry:
        """Load a given metric entry."""
        return self._row_to_entity(self._storage.load(ref_id, allow_archived=allow_archived))

    def find_all_for_metric(self, metric_ref_id: EntityId, allow_archived: bool = False) -> typing.List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    metric_ref_id=Eq(metric_ref_id))]

    def find_all(
            self, allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> typing.List[MetricEntry]:
        """Find all metric entries matching some criteria."""
        return [self._row_to_entity(mer)
                for mer in self._storage.find_all(
                    allow_archived=allow_archived,
                    ref_id=In(*filter_ref_ids) if filter_ref_ids else None,
                    metric_ref_id=In(*filter_metric_ref_ids) if filter_metric_ref_ids else None)]

    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric - an irreversible operation."""
        return self._row_to_entity(self._storage.remove(ref_id=ref_id))

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
    def storage_to_live(storage_form: JSONDictType) -> _MetricEntryRow:
        """Transform the data reconstructed from basic storage into something useful for the live system."""
        return _MetricEntryRow(
            metric_ref_id=EntityId(typing.cast(str, storage_form["metric_ref_id"])),
            collection_time=BasicValidator.adate_from_str(typing.cast(str, storage_form["collection_time"])),
            value=typing.cast(float, storage_form["value"]),
            notes=typing.cast(str, storage_form["notes"]) if storage_form.get("notes", None) else None,
            archived=typing.cast(bool, storage_form["archived"]))

    @staticmethod
    def live_to_storage(live_form: _MetricEntryRow) -> JSONDictType:
        """Transform the live system data to something suitable for basic storage."""
        return {
            "metric_ref_id": live_form.metric_ref_id,
            "collection_time": BasicValidator.adate_to_str(live_form.collection_time),
            "value": live_form.value,
            "notes": live_form.notes
        }

    @staticmethod
    def _entity_to_row(metric_entry: MetricEntry) -> _MetricEntryRow:
        metric_entry_row = _MetricEntryRow(
            archived=metric_entry.archived,
            metric_ref_id=metric_entry.metric_ref_id,
            collection_time=metric_entry.collection_time,
            value=metric_entry.value,
            notes=metric_entry.notes)
        metric_entry_row.ref_id = metric_entry.ref_id
        metric_entry_row.created_time = metric_entry.created_time
        metric_entry_row.archived_time = metric_entry.archived_time
        metric_entry_row.last_modified_time = metric_entry.last_modified_time
        return metric_entry_row

    @staticmethod
    def _row_to_entity(row: _MetricEntryRow) -> MetricEntry:
        return MetricEntry(
            _ref_id=row.ref_id,
            _archived=row.archived,
            _created_time=row.created_time,
            _archived_time=row.archived_time,
            _last_modified_time=row.last_modified_time,
            _events=[],
            _metric_ref_id=row.metric_ref_id,
            _collection_time=row.collection_time,
            _value=row.value,
            _notes=row.notes)


class YamlMetricUnitOfWork(MetricUnitOfWork):
    """A Yaml text file specific metric unit of work."""

    _metric_repository: Final[YamlMetricRepository]
    _metric_entry_repository: Final[YamlMetricEntryRepository]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._metric_repository = YamlMetricRepository(time_provider)
        self._metric_entry_repository = YamlMetricEntryRepository(time_provider)

    def __enter__(self) -> 'YamlMetricUnitOfWork':
        """Enter context."""
        self._metric_repository.initialize()
        self._metric_entry_repository.initialize()
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""
        return self._metric_repository

    @property
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""
        return self._metric_entry_repository


class YamlMetricEngine(MetricEngine):
    """An Yaml text file specific metric engine."""

    _time_provider: Final[TimeProvider]

    def __init__(self, time_provider: TimeProvider) -> None:
        """Constructor."""
        self._time_provider = time_provider

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[MetricUnitOfWork]:
        """Get the unit of work."""
        yield YamlMetricUnitOfWork(self._time_provider)
