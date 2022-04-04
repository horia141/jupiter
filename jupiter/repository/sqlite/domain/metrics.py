"""SQLite based metrics repositories."""
import logging
from typing import Optional, Iterable, List, Final

from sqlalchemy import (
    insert,
    MetaData,
    Table,
    Column,
    Integer,
    Boolean,
    DateTime,
    String,
    Unicode,
    ForeignKey,
    Float,
    UnicodeText,
    update,
    select,
    delete,
)
from sqlalchemy.engine import Connection, Result
from sqlalchemy.exc import IntegrityError

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
    MetricCollectionNotFoundError,
)
from jupiter.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
    MetricEntryNotFoundError,
)
from jupiter.domain.metrics.infra.metric_repository import (
    MetricRepository,
    MetricAlreadyExistsError,
    MetricNotFoundError,
)
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.repository.sqlite.infra.events import (
    build_event_table,
    upsert_events,
    remove_events,
)

LOGGER = logging.getLogger(__name__)


class SqliteMetricCollectionRepository(MetricCollectionRepository):
    """The metric collection repository."""

    _connection: Final[Connection]
    _metric_collection_table: Final[Table]
    _metric_collection_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._metric_collection_table = Table(
            "metric_collection",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "workspace_ref_id",
                Integer,
                ForeignKey("workspace.ref_id"),
                unique=True,
                index=True,
                nullable=False,
            ),
            Column(
                "collection_project_ref_id",
                Integer,
                ForeignKey("project.ref_id"),
                nullable=False,
            ),
            keep_existing=True,
        )
        self._metric_collection_event_table = build_event_table(
            self._metric_collection_table, metadata
        )

    def create(self, entity: MetricCollection) -> MetricCollection:
        """Create a metric collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._metric_collection_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                collection_project_ref_id=entity.collection_project_ref_id.as_int(),
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._metric_collection_event_table, entity)
        return entity

    def save(self, entity: MetricCollection) -> MetricCollection:
        """Save a big metric collection."""
        result = self._connection.execute(
            update(self._metric_collection_table)
            .where(self._metric_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                collection_project_ref_id=entity.collection_project_ref_id.as_int(),
            )
        )
        if result.rowcount == 0:
            raise MetricCollectionNotFoundError("The metric collection does not exist")
        upsert_events(self._connection, self._metric_collection_event_table, entity)
        return entity

    def load_by_parent(self, parent_ref_id: EntityId) -> MetricCollection:
        """Load a metric collection for a given metric."""
        query_stmt = select(self._metric_collection_table).where(
            self._metric_collection_table.c.workspace_ref_id == parent_ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricCollectionNotFoundError(
                f"Big plan collection for metric {parent_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> MetricCollection:
        return MetricCollection(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            workspace_ref_id=EntityId.from_raw(str(row["workspace_ref_id"])),
            collection_project_ref_id=EntityId.from_raw(
                str(row["collection_project_ref_id"])
            ),
        )


class SqliteMetricRepository(MetricRepository):
    """A repository for metrics."""

    _connection: Final[Connection]
    _metric_table: Final[Table]
    _metric_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._metric_table = Table(
            "metric",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "metric_collection_ref_id",
                Integer,
                ForeignKey("metric_collection.ref_id"),
                nullable=False,
            ),
            Column("the_key", String(64), nullable=False, index=True, unique=True),
            Column("name", Unicode(), nullable=False),
            Column("icon", String(1), nullable=True),
            Column("collection_project_ref_id", Integer, nullable=True),
            Column("collection_period", String, nullable=True),
            Column("collection_eisen", String, nullable=True),
            Column("collection_difficulty", String, nullable=True),
            Column("collection_actionable_from_day", Integer, nullable=True),
            Column("collection_actionable_from_month", Integer, nullable=True),
            Column("collection_due_at_time", String, nullable=True),
            Column("collection_due_at_day", Integer, nullable=True),
            Column("collection_due_at_month", Integer, nullable=True),
            Column("metric_unit", String(), nullable=True),
            keep_existing=True,
        )
        self._metric_event_table = build_event_table(self._metric_table, metadata)

    def create(self, entity: Metric) -> Metric:
        """Create a metric."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = self._connection.execute(
                insert(self._metric_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    metric_collection_ref_id=entity.metric_collection_ref_id.as_int(),
                    the_key=str(entity.key),
                    name=str(entity.name),
                    icon=entity.icon.to_safe() if entity.icon else None,
                    collection_period=entity.collection_params.period.value
                    if entity.collection_params
                    else None,
                    collection_eisen=entity.collection_params.eisen.value
                    if entity.collection_params
                    else None,
                    collection_difficulty=entity.collection_params.difficulty.value
                    if entity.collection_params and entity.collection_params.difficulty
                    else None,
                    collection_actionable_from_day=entity.collection_params.actionable_from_day.as_int()
                    if entity.collection_params
                    and entity.collection_params.actionable_from_day
                    else None,
                    collection_actionable_from_month=entity.collection_params.actionable_from_month.as_int()
                    if entity.collection_params
                    and entity.collection_params.actionable_from_month
                    else None,
                    collection_due_at_time=str(entity.collection_params.due_at_time)
                    if entity.collection_params and entity.collection_params.due_at_time
                    else None,
                    collection_due_at_day=entity.collection_params.due_at_day.as_int()
                    if entity.collection_params and entity.collection_params.due_at_day
                    else None,
                    collection_due_at_month=entity.collection_params.due_at_month.as_int()
                    if entity.collection_params
                    and entity.collection_params.due_at_month
                    else None,
                    metric_unit=entity.metric_unit.value
                    if entity.metric_unit
                    else None,
                )
            )
        except IntegrityError as err:
            raise MetricAlreadyExistsError(
                f"Metric with key {entity.key} already exists"
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._metric_event_table, entity)
        return entity

    def save(self, entity: Metric) -> Metric:
        """Save a metric - it should already exist."""
        result = self._connection.execute(
            update(self._metric_table)
            .where(self._metric_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                metric_collection_ref_id=entity.metric_collection_ref_id.as_int(),
                the_key=str(entity.key),
                name=str(entity.name),
                icon=entity.icon.to_safe() if entity.icon else None,
                collection_period=entity.collection_params.period.value
                if entity.collection_params
                else None,
                collection_eisen=entity.collection_params.eisen.value
                if entity.collection_params
                else None,
                collection_difficulty=entity.collection_params.difficulty.value
                if entity.collection_params and entity.collection_params.difficulty
                else None,
                collection_actionable_from_day=entity.collection_params.actionable_from_day.as_int()
                if entity.collection_params
                and entity.collection_params.actionable_from_day
                else None,
                collection_actionable_from_month=entity.collection_params.actionable_from_month.as_int()
                if entity.collection_params
                and entity.collection_params.actionable_from_month
                else None,
                collection_due_at_time=str(entity.collection_params.due_at_time)
                if entity.collection_params and entity.collection_params.due_at_time
                else None,
                collection_due_at_day=entity.collection_params.due_at_day.as_int()
                if entity.collection_params and entity.collection_params.due_at_day
                else None,
                collection_due_at_month=entity.collection_params.due_at_month.as_int()
                if entity.collection_params and entity.collection_params.due_at_month
                else None,
                metric_unit=entity.metric_unit.value if entity.metric_unit else None,
            )
        )
        if result.rowcount == 0:
            raise MetricNotFoundError(f"Metric with key {entity.key} does not exist")
        upsert_events(self._connection, self._metric_event_table, entity)
        return entity

    def load_by_key(self, parent_ref_id: EntityId, key: MetricKey) -> Metric:
        """Find a metric by key."""
        query_stmt = (
            select(self._metric_table)
            .where(
                self._metric_table.c.metric_collection_ref_id == parent_ref_id.as_int()
            )
            .where(self._metric_table.c.the_key == str(key))
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with key {key} does not exist")
        return self._row_to_entity(result)

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> Metric:
        """Find a metric by id."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.ref_id == ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        return self._row_to_entity(result)

    def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_keys: Optional[Iterable[MetricKey]] = None,
    ) -> List[Metric]:
        """Find all metrics matching some criteria."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.metric_collection_ref_id == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._metric_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids)
            )
        if filter_keys:
            query_stmt = query_stmt.where(
                self._metric_table.c.the_key.in_(str(k) for k in filter_keys)
            )
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric - an irreversible operation."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.ref_id == ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        self._connection.execute(
            delete(self._metric_table).where(
                self._metric_table.c.ref_id == ref_id.as_int()
            )
        )
        remove_events(self._connection, self._metric_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> Metric:
        return Metric(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            metric_collection_ref_id=EntityId.from_raw(
                str(row["metric_collection_ref_id"])
            ),
            key=MetricKey.from_raw(row["the_key"]),
            name=MetricName.from_raw(row["name"]),
            icon=EntityIcon.from_safe(row["icon"]) if row["icon"] else None,
            collection_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["collection_period"]),
                eisen=Eisen.from_raw(row["collection_eisen"]),
                difficulty=Difficulty.from_raw(row["collection_difficulty"])
                if row["collection_difficulty"]
                else None,
                actionable_from_day=RecurringTaskDueAtDay(
                    row["collection_actionable_from_day"]
                )
                if row["collection_actionable_from_day"] is not None
                else None,
                actionable_from_month=RecurringTaskDueAtMonth(
                    row["collection_actionable_from_month"]
                )
                if row["collection_actionable_from_month"] is not None
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(
                    row["collection_due_at_time"]
                )
                if row["collection_due_at_time"] is not None
                else None,
                due_at_day=RecurringTaskDueAtDay(row["collection_due_at_day"])
                if row["collection_due_at_day"] is not None
                else None,
                due_at_month=RecurringTaskDueAtMonth(row["collection_due_at_month"])
                if row["collection_due_at_month"] is not None
                else None,
            )
            if row["collection_project_ref_id"] is not None
            and row["collection_period"] is not None
            else None,
            metric_unit=MetricUnit.from_raw(row["metric_unit"])
            if row["metric_unit"]
            else None,
        )


class SqliteMetricEntryRepository(MetricEntryRepository):
    """A repository of metric entries."""

    _connection: Final[Connection]
    _metric_entry_table: Final[Table]
    _metric_entry_event_table: Final[Table]

    def __init__(self, connection: Connection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._metric_entry_table = Table(
            "metric_entry",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "metric_ref_id", ForeignKey("metric.ref_id"), index=True, nullable=False
            ),
            Column("collection_time", DateTime, nullable=False),
            Column("value", Float, nullable=False),
            Column("notes", UnicodeText, nullable=True),
            keep_existing=True,
        )
        self._metric_entry_event_table = build_event_table(
            self._metric_entry_table, metadata
        )

    def create(self, entity: MetricEntry) -> MetricEntry:
        """Create a metric entry."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = self._connection.execute(
            insert(self._metric_entry_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                metric_ref_id=entity.metric_ref_id.as_int(),
                collection_time=entity.collection_time.to_db(),
                value=entity.value,
                notes=entity.notes,
            )
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        upsert_events(self._connection, self._metric_entry_event_table, entity)
        return entity

    def save(self, entity: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""
        result = self._connection.execute(
            update(self._metric_entry_table)
            .where(self._metric_entry_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                metric_ref_id=entity.metric_ref_id.as_int(),
                collection_time=entity.collection_time.to_db(),
                value=entity.value,
                notes=entity.notes,
            )
        )
        if result.rowcount == 0:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {entity.ref_id} does not exist"
            )
        upsert_events(self._connection, self._metric_entry_event_table, entity)
        return entity

    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> MetricEntry:
        """Load a given metric entry."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.ref_id == ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.archived.is_(False)
            )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {ref_id} does not exist"
            )
        return self._row_to_entity(result)

    def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.metric_ref_id == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.archived.is_(False)
            )
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.ref_id.in_(
                    fi.as_int() for fi in filter_ref_ids
                )
            )
        results = self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric entry - an irreversible operation."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.ref_id == ref_id.as_int()
        )
        result = self._connection.execute(query_stmt).first()
        if result is None:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {ref_id} does not exist"
            )
        self._connection.execute(
            delete(self._metric_entry_table).where(
                self._metric_entry_table.c.ref_id == ref_id.as_int()
            )
        )
        remove_events(self._connection, self._metric_entry_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: Result) -> MetricEntry:
        return MetricEntry(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            metric_ref_id=EntityId.from_raw(str(row["metric_ref_id"])),
            collection_time=ADate.from_db(row["collection_time"]),
            value=row["value"],
            notes=row["notes"],
        )
