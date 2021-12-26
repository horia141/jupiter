"""SQLite based metrics repositories."""
import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable, List, Final, Iterator

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, insert, MetaData, Table, Column, Integer, Boolean, DateTime, String, Unicode, \
    ForeignKey, Float, UnicodeText, JSON, update, select, delete
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Engine

from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.metrics.infra.metric_engine import MetricUnitOfWork, MetricEngine
from domain.metrics.infra.metric_entry_repository import MetricEntryRepository, MetricEntryNotFoundError
from domain.metrics.infra.metric_repository import MetricRepository, MetricAlreadyExistsError, MetricNotFoundError
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.metrics.metric_key import MetricKey
from domain.metrics.metric_unit import MetricUnit
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from framework.base.entity_id import EntityId, BAD_REF_ID
from framework.base.timestamp import Timestamp
from repository.sqlite.infra.events import build_event_table, upsert_events

LOGGER = logging.getLogger(__name__)


class SqliteMetricRepository(MetricRepository):
    """A repository for metrics."""

    _connection: Final[Connection]
    _metric_table: Final[Table]
    _metric_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._metric_table = Table(
            'metric',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True),
            Column('the_key', String(64), nullable=False, index=True, unique=True),
            Column('name', Unicode(), nullable=False),
            Column('collection_project_ref_id', Integer, nullable=True),
            Column('collection_period', String(), nullable=True),
            Column('collection_eisen', JSON, nullable=True),
            Column('collection_difficulty', String, nullable=True),
            Column('collection_actionable_from_day', Integer, nullable=True),
            Column('collection_actionable_from_month', Integer, nullable=True),
            Column('collection_due_at_time', String, nullable=True),
            Column('collection_due_at_day', Integer, nullable=True),
            Column('collection_due_at_month', Integer, nullable=True),
            Column('metric_unit', String(), nullable=True),
            keep_existing=True)
        self._metric_event_table = build_event_table(self._metric_table, metadata)

    def create(self, metric: Metric) -> Metric:
        """Create a metric."""
        try:
            result = self._connection.execute(insert(self._metric_table).values(
                ref_id=metric.ref_id.as_int() if metric.ref_id != BAD_REF_ID else None,
                archived=metric.archived,
                created_time=metric.created_time.to_db(),
                last_modified_time=metric.last_modified_time.to_db(),
                archived_time=metric.archived_time.to_db()
                if metric.archived_time else None,
                the_key=str(metric.key),
                name=str(metric.name),
                collection_project_ref_id=
                metric.collection_params.project_ref_id.as_int() if metric.collection_params else None,
                collection_period=metric.collection_params.period.value if metric.collection_params else None,
                collection_eisen=[e.value for e in metric.collection_params.eisen] if metric.collection_params else [],
                collection_difficulty=metric.collection_params.difficulty.value
                if metric.collection_params and metric.collection_params.difficulty else None,
                collection_actionable_from_day=metric.collection_params.actionable_from_day.as_int()
                if metric.collection_params and metric.collection_params.actionable_from_day else None,
                collection_actionable_from_month=metric.collection_params.actionable_from_month.as_int()
                if metric.collection_params and metric.collection_params.actionable_from_month else None,
                collection_due_at_time=str(metric.collection_params.due_at_time)
                if metric.collection_params and metric.collection_params.due_at_time else None,
                collection_due_at_day=metric.collection_params.due_at_day.as_int()
                if metric.collection_params and metric.collection_params.due_at_day else None,
                collection_due_at_month=metric.collection_params.due_at_month.as_int()
                if metric.collection_params and metric.collection_params.due_at_month else None,
                metric_unit=metric.metric_unit.value if metric.metric_unit else None))
        except IntegrityError as err:
            raise MetricAlreadyExistsError(f"Metric with key {metric.key} already exists") from err
        metric.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._metric_event_table, metric)
        return metric

    def save(self, metric: Metric) -> Metric:
        """Save a metric - it should already exist."""
        result = self._connection.execute(
            update(self._metric_table)
            .where(self._metric_table.c.ref_id == metric.ref_id.as_int())
            .values(
                archived=metric.archived,
                created_time=metric.created_time.to_db(),
                last_modified_time=metric.last_modified_time.to_db(),
                archived_time=metric.archived_time.to_db() if metric.archived_time else None,
                the_key=str(metric.key),
                name=str(metric.name),
                collection_project_ref_id=metric.collection_params.project_ref_id.as_int()
                if metric.collection_params else None,
                collection_period=metric.collection_params.period.value if metric.collection_params else None,
                collection_eisen=[e.value for e in metric.collection_params.eisen] if metric.collection_params else [],
                collection_difficulty=metric.collection_params.difficulty.value
                if metric.collection_params and metric.collection_params.difficulty else None,
                collection_actionable_from_day=metric.collection_params.actionable_from_day.as_int()
                if metric.collection_params and metric.collection_params.actionable_from_day else None,
                collection_actionable_from_month=metric.collection_params.actionable_from_month.as_int()
                if metric.collection_params and metric.collection_params.actionable_from_month else None,
                collection_due_at_time=str(metric.collection_params.due_at_time)
                if metric.collection_params and metric.collection_params.due_at_time else None,
                collection_due_at_day=metric.collection_params.due_at_day.as_int()
                if metric.collection_params and metric.collection_params.due_at_day else None,
                collection_due_at_month=metric.collection_params.due_at_month.as_int()
                if metric.collection_params and metric.collection_params.due_at_month else None,
                metric_unit=metric.metric_unit.value if metric.metric_unit else None))
        if result.rowcount == 0:
            raise MetricNotFoundError(f"Metric with key {metric.key} does not exist")
        upsert_events(self._connection, self._metric_event_table, metric)
        return metric

    def load_by_key(self, key: MetricKey) -> Metric:
        """Find a metric by key."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.the_key == str(key))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with key {key} does not exist")
        return self._row_to_entity(result)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
        """Find a metric by id."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[MetricKey]] = None) -> List[Metric]:
        """Find all metrics matching some criteria."""
        query_stmt = select(self._metric_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._metric_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_keys:
            query_stmt = query_stmt.where(
                self._metric_table.c.the_key.in_(str(k) for k in filter_keys))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric - an irreversible operation."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        self._connection.execute(delete(self._metric_table).where(self._metric_table.c.ref_id == ref_id.as_int()))
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Metric:
        return Metric(
            _ref_id=EntityId.from_raw(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=Timestamp.from_db(row["created_time"]),
            _archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            _events=[],
            _key=MetricKey.from_raw(row["the_key"]),
            _name=EntityName.from_raw(row["name"]),
            _collection_params=RecurringTaskGenParams(
                project_ref_id=EntityId.from_raw(str(row["collection_project_ref_id"])),
                period=RecurringTaskPeriod.from_raw(row["collection_period"]),
                eisen=[Eisen.from_raw(e) for e in row["collection_eisen"]],
                difficulty=Difficulty.from_raw(row["collection_difficulty"])
                if row["collection_difficulty"] else None,
                actionable_from_day=RecurringTaskDueAtDay(row["collection_actionable_from_day"])
                if row["collection_actionable_from_day"] is not None else None,
                actionable_from_month=RecurringTaskDueAtMonth(row["collection_actionable_from_month"])
                if row["collection_actionable_from_month"] is not None else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(row["collection_due_at_time"])
                if row["collection_due_at_time"] is not None else None,
                due_at_day=RecurringTaskDueAtDay(row["collection_due_at_day"])
                if row["collection_due_at_day"] is not None else None,
                due_at_month=RecurringTaskDueAtMonth(row["collection_due_at_month"])
                if row["collection_due_at_month"] is not None else None)
            if row["collection_project_ref_id"] is not None and row["collection_period"] is not None else None,
            _metric_unit=MetricUnit.from_raw(row["metric_unit"])
            if row["metric_unit"] else None)


class SqliteMetricEntryRepository(MetricEntryRepository):
    """A repository of metric entries."""

    _connection: Final[Connection]
    _metric_entry_table: Final[Table]
    _metric_entry_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._metric_entry_table = Table(
            'metric_entry',
            metadata,
            Column('ref_id', Integer, primary_key=True, autoincrement=True),
            Column('archived', Boolean, nullable=False),
            Column('created_time', DateTime, nullable=False),
            Column('last_modified_time', DateTime, nullable=False),
            Column('archived_time', DateTime, nullable=True, index=True),
            Column('metric_ref_id', ForeignKey('metric.ref_id'), nullable=False),
            Column('collection_time', DateTime, nullable=False),
            Column('value', Float, nullable=False),
            Column('notes', UnicodeText, nullable=True),
            keep_existing=True)
        self._metric_entry_event_table = build_event_table(self._metric_entry_table, metadata)

    def create(self, metric_entry: MetricEntry) -> MetricEntry:
        """Create a metric entry."""
        result = self._connection.execute(insert(self._metric_entry_table).values(
            ref_id=metric_entry.ref_id.as_int() if metric_entry.ref_id != BAD_REF_ID else None,
            archived=metric_entry.archived,
            created_time=metric_entry.created_time.to_db(),
            last_modified_time=metric_entry.last_modified_time.to_db(),
            archived_time=metric_entry.archived_time.to_db() if metric_entry.archived_time else None,
            metric_ref_id=metric_entry.metric_ref_id.as_int(),
            collection_time=metric_entry.collection_time.to_db(),
            value=metric_entry.value,
            notes=metric_entry.notes))
        metric_entry.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._metric_entry_event_table, metric_entry)
        return metric_entry

    def save(self, metric_entry: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""
        result = self._connection.execute(
            update(self._metric_entry_table)
            .where(self._metric_entry_table.c.ref_id == metric_entry.ref_id.as_int())
            .values(
                archived=metric_entry.archived,
                created_time=metric_entry.created_time.to_db(),
                last_modified_time=metric_entry.last_modified_time.to_db(),
                archived_time=metric_entry.archived_time.to_db() if metric_entry.archived_time else None,
                metric_ref_id=metric_entry.metric_ref_id.as_int(),
                collection_time=metric_entry.collection_time.to_db(),
                value=metric_entry.value,
                notes=metric_entry.notes))
        if result.rowcount == 0:
            raise MetricEntryNotFoundError(f"Metric entry with id {metric_entry.ref_id} does not exist")
        upsert_events(self._connection, self._metric_entry_event_table, metric_entry)
        return metric_entry

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntry:
        """Load a given metric entry."""
        query_stmt = select(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_entry_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricEntryNotFoundError(f"Metric entry with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all_for_metric(self, metric_ref_id: EntityId, allow_archived: bool = False) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""
        query_stmt = select(self._metric_entry_table)\
            .where(self._metric_entry_table.c.metric_ref_id == metric_ref_id.as_int())
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_entry_table.c.archived.is_(False))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def find_all(
            self,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_metric_ref_ids: Optional[Iterable[EntityId]] = None) -> List[MetricEntry]:
        """Find all metric entries matching some criteria."""
        query_stmt = select(self._metric_entry_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_entry_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(self._metric_entry_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids))
        if filter_metric_ref_ids:
            query_stmt = query_stmt\
                .where(self._metric_entry_table.c.metric_ref_id.in_(fi.as_int() for fi in filter_metric_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric entry - an irreversible operation."""
        query_stmt = select(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id.as_int())
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricEntryNotFoundError(f"Metric entry with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id.as_int()))
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> MetricEntry:
        return MetricEntry(
            _ref_id=EntityId.from_raw(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=Timestamp.from_db(row["created_time"]),
            _archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            _events=[],
            _metric_ref_id=EntityId.from_raw(str(row["metric_ref_id"])),
            _collection_time=ADate.from_db(row["collection_time"]),
            _value=row["value"],
            _notes=row["notes"])


class SqliteMetricUnitOfWork(MetricUnitOfWork):
    """A Sqlite specific metric unit of work."""

    _metric_repository: Final[SqliteMetricRepository]
    _metric_entry_repository: Final[SqliteMetricEntryRepository]

    def __init__(
            self, metric_repository: SqliteMetricRepository,
            metric_entry_repository: SqliteMetricEntryRepository) -> None:
        """Constructor."""
        self._metric_repository = metric_repository
        self._metric_entry_repository = metric_entry_repository

    @property
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""
        return self._metric_repository

    @property
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""
        return self._metric_entry_repository


class SqliteMetricEngine(MetricEngine):
    """An Sqlite specific metric engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_engine(config.sqlite_db_url, future=True, json_serializer=json.dumps)
        self._metadata = MetaData(bind=self._sql_engine)

    def prepare(self) -> None:
        """Prepare the environment for SQLite."""
        with self._sql_engine.begin() as connection:
            alembic_cfg = Config(str(self._config.alembic_ini_path))
            alembic_cfg.set_section_option('alembic', 'script_location', str(self._config.alembic_migrations_path))
            # pylint: disable=unsupported-assignment-operation
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, 'head')

    @contextmanager
    def get_unit_of_work(self) -> Iterator[MetricUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            metric_repository = SqliteMetricRepository(connection, self._metadata)
            metric_entry_repository = SqliteMetricEntryRepository(connection, self._metadata)
            yield SqliteMetricUnitOfWork(metric_repository, metric_entry_repository)
