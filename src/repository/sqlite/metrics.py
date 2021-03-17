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
from sqlalchemy.dialects.sqlite import insert as sqliteInsert
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import Engine

from domain.metrics.infra.metric_engine import MetricUnitOfWork, MetricEngine
from domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from domain.metrics.infra.metric_repository import MetricRepository
from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from models.basic import MetricKey, EntityId, BasicValidator
from models.framework import AggregateRoot, RepositoryError, BAD_REF_ID
from utils.storage import StructuredStorageError

LOGGER = logging.getLogger(__name__)


def _build_event_table(entity_table: Table, metadata: MetaData) -> Table:
    return Table(
        entity_table.name + '_event',
        metadata,
        Column('owner_ref_id', Integer, ForeignKey(entity_table.c.ref_id), primary_key=True),
        Column('timestamp', DateTime, primary_key=True),
        Column('session_index', Integer, primary_key=True),
        Column('name', String(32), primary_key=True),
        Column('data', JSON, nullable=True),
        keep_existing=True)


def _upsert_events(connection: Connection, table: Table, entity: AggregateRoot) -> None:
    for event_idx, event in enumerate(entity.events):
        connection.execute(
            sqliteInsert(table)
            .values(
                owner_ref_id=int(entity.ref_id),
                timestamp=event.timestamp,
                session_index=event_idx,
                name=str(event.__class__.__name__),
                data=event.to_serializable_dict())
            .on_conflict_do_nothing(index_elements=['owner_ref_id', 'timestamp', 'session_index', 'name']))


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
            Column('collection_period', String(), nullable=True),
            Column('metric_unit', String(), nullable=True),
            keep_existing=True)
        self._metric_event_table = _build_event_table(self._metric_table, metadata)

    def create(self, metric: Metric) -> Metric:
        """Create a metric."""
        try:
            result = self._connection.execute(insert(self._metric_table).values(
                ref_id=metric.ref_id if metric.ref_id != BAD_REF_ID else None,
                archived=metric.archived,
                created_time=BasicValidator.timestamp_to_db_timestamp(metric.created_time),
                last_modified_time=BasicValidator.timestamp_to_db_timestamp(metric.last_modified_time),
                archived_time=BasicValidator.timestamp_to_db_timestamp(metric.archived_time)
                if metric.archived_time else None,
                the_key=metric.key,
                name=metric.name,
                collection_period=metric.collection_period.value if metric.collection_period else None,
                metric_unit=metric.metric_unit.value if metric.metric_unit else None))
        except IntegrityError as err:
            raise RepositoryError(f"Metric with key='{metric.key}' already exists") from err
        metric.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        _upsert_events(self._connection, self._metric_event_table, metric)
        return metric

    def save(self, metric: Metric) -> Metric:
        """Save a metric - it should already exist."""
        self._connection.execute(
            update(self._metric_table)
            .where(self._metric_table.c.ref_id == metric.ref_id)
            .values(
                archived=metric.archived,
                created_time=BasicValidator.timestamp_to_db_timestamp(metric.created_time),
                last_modified_time=BasicValidator.timestamp_to_db_timestamp(metric.last_modified_time),
                archived_time=BasicValidator.timestamp_to_db_timestamp(metric.archived_time)
                if metric.archived_time else None,
                the_key=metric.key,
                name=metric.name,
                collection_period=metric.collection_period.value if metric.collection_period else None,
                metric_unit=metric.metric_unit.value if metric.metric_unit else None))
        _upsert_events(self._connection, self._metric_event_table, metric)
        return metric

    def get_by_key(self, key: MetricKey) -> Metric:
        """Find a metric by key."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.the_key == key)
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise StructuredStorageError(f"Metric identified by key={key} does not exist or is archived")
        return self._row_to_entity(result)

    def get_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
        """Find a metric by id."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.ref_id == ref_id)
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise StructuredStorageError(f"Metric identified by {ref_id} does not exist or is archived")
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
            query_stmt = query_stmt.where(self._metric_table.c.ref_id.in_(int(fi) for fi in filter_ref_ids))
        if filter_keys:
            query_stmt = query_stmt.where(
                self._metric_table.c.the_key.in_(filter_keys))
        LOGGER.info(query_stmt)
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric - an irreversible operation."""
        query_stmt = select(self._metric_table).where(self._metric_table.c.ref_id == ref_id)
        result = self._connection.execute(query_stmt).first()
        self._connection.execute(delete(self._metric_table).where(self._metric_table.c.ref_id == ref_id))
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Metric:
        return Metric(
            _ref_id=EntityId(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=BasicValidator.timestamp_from_db_timestamp(row["created_time"]),
            _archived_time=BasicValidator.timestamp_from_db_timestamp(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=BasicValidator.timestamp_from_db_timestamp(row["last_modified_time"]),
            _events=[],
            _key=BasicValidator.metric_key_validate_and_clean(row["the_key"]),
            _name=BasicValidator.entity_name_validate_and_clean(row["name"]),
            _collection_period=BasicValidator.recurring_task_period_validate_and_clean(row["collection_period"])
            if row["collection_period"] else None,
            _metric_unit=BasicValidator.metric_unit_validate_and_clean(row["metric_unit"])
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
        self._metric_entry_event_table = _build_event_table(self._metric_entry_table, metadata)

    def create(self, metric_entry: MetricEntry) -> MetricEntry:
        """Create a metric entry."""
        result = self._connection.execute(insert(self._metric_entry_table).values(
            ref_id=metric_entry.ref_id if metric_entry.ref_id != BAD_REF_ID else None,
            archived=metric_entry.archived,
            created_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.created_time),
            last_modified_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.last_modified_time),
            archived_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.archived_time)
            if metric_entry.archived_time else None,
            metric_ref_id=metric_entry.metric_ref_id,
            collection_time=metric_entry.collection_time,
            value=metric_entry.value,
            notes=metric_entry.notes))
        metric_entry.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        _upsert_events(self._connection, self._metric_entry_event_table, metric_entry)
        return metric_entry

    def save(self, metric_entry: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""
        self._connection.execute(
            update(self._metric_entry_table)
            .where(self._metric_entry_table.c.ref_id == metric_entry.ref_id)
            .values(
                archived=metric_entry.archived,
                created_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.created_time),
                last_modified_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.last_modified_time),
                archived_time=BasicValidator.timestamp_to_db_timestamp(metric_entry.archived_time)
                if metric_entry.archived_time else None,
                metric_ref_id=metric_entry.metric_ref_id,
                collection_time=metric_entry.collection_time,
                value=metric_entry.value,
                notes=metric_entry.notes))
        _upsert_events(self._connection, self._metric_entry_event_table, metric_entry)
        return metric_entry

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntry:
        """Load a given metric entry."""
        query_stmt = select(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id)
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_entry_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise StructuredStorageError(f"Metric entry identified by {ref_id} does not exist or is archived")
        return self._row_to_entity(result)

    def find_all_for_metric(self, metric_ref_id: EntityId, allow_archived: bool = False) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""
        query_stmt = select(self._metric_entry_table)\
            .where(self._metric_entry_table.c.metric_ref_id == metric_ref_id)
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
            query_stmt = query_stmt.where(self._metric_entry_table.c.ref_id.in_(int(fi) for fi in filter_ref_ids))
        if filter_metric_ref_ids:
            query_stmt = query_stmt\
                .where(self._metric_entry_table.c.metric_ref_id.in_(int(fi) for fi in filter_metric_ref_ids))
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric entry - an irreversible operation."""
        query_stmt = select(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id)
        result = self._connection.execute(query_stmt).first()
        self._connection.execute(delete(self._metric_entry_table).where(self._metric_entry_table.c.ref_id == ref_id))
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> MetricEntry:
        return MetricEntry(
            _ref_id=EntityId(str(row["ref_id"])),
            _archived=row["archived"],
            _created_time=BasicValidator.timestamp_from_db_timestamp(row["created_time"]),
            _archived_time=BasicValidator.timestamp_from_db_timestamp(row["archived_time"])
            if row["archived_time"] else None,
            _last_modified_time=BasicValidator.timestamp_from_db_timestamp(row["last_modified_time"]),
            _events=[],
            _metric_ref_id=EntityId(row["metric_ref_id"]),
            _collection_time=BasicValidator.timestamp_from_db_timestamp(row["collection_time"]),
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
