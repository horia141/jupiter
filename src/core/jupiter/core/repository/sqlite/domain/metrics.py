"""SQLite based metrics repositories."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.difficulty import Difficulty
from jupiter.core.domain.core.eisen import Eisen
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.core.domain.core.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.core.domain.core.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionNotFoundError,
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryNotFoundError,
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import (
    MetricNotFoundError,
    MetricRepository,
)
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Unicode,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteMetricCollectionRepository(MetricCollectionRepository):
    """The metric collection repository."""

    _connection: Final[AsyncConnection]
    _metric_collection_table: Final[Table]
    _metric_collection_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
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
            self._metric_collection_table,
            metadata,
        )

    async def create(self, entity: MetricCollection) -> MetricCollection:
        """Create a metric collection."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
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
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._metric_collection_event_table,
            entity,
        )
        return entity

    async def save(self, entity: MetricCollection) -> MetricCollection:
        """Save a big metric collection."""
        result = await self._connection.execute(
            update(self._metric_collection_table)
            .where(self._metric_collection_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
                collection_project_ref_id=entity.collection_project_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise MetricCollectionNotFoundError("The metric collection does not exist")
        await upsert_events(
            self._connection,
            self._metric_collection_event_table,
            entity,
        )
        return entity

    async def load_by_parent(self, parent_ref_id: EntityId) -> MetricCollection:
        """Load a metric collection for a given metric."""
        query_stmt = select(self._metric_collection_table).where(
            self._metric_collection_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise MetricCollectionNotFoundError(
                f"Big plan collection for metric {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> MetricCollection:
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
                str(row["collection_project_ref_id"]),
            ),
        )


class SqliteMetricRepository(MetricRepository):
    """A repository for metrics."""

    _connection: Final[AsyncConnection]
    _metric_table: Final[Table]
    _metric_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
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
            Column("name", Unicode(), nullable=False),
            Column("icon", String(1), nullable=True),
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

    async def create(self, entity: Metric) -> Metric:
        """Create a metric."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
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
                name=str(entity.name),
                icon=entity.icon.to_safe() if entity.icon else None,
                collection_period=entity.collection_params.period.value
                if entity.collection_params
                else None,
                collection_eisen=entity.collection_params.eisen.value
                if entity.collection_params and entity.collection_params.eisen
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
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._metric_event_table, entity)
        return entity

    async def save(self, entity: Metric) -> Metric:
        """Save a metric - it should already exist."""
        result = await self._connection.execute(
            update(self._metric_table)
            .where(self._metric_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                metric_collection_ref_id=entity.metric_collection_ref_id.as_int(),
                name=str(entity.name),
                icon=entity.icon.to_safe() if entity.icon else None,
                collection_period=entity.collection_params.period.value
                if entity.collection_params
                else None,
                collection_eisen=entity.collection_params.eisen.value
                if entity.collection_params and entity.collection_params.eisen
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
            ),
        )
        if result.rowcount == 0:
            raise MetricNotFoundError(f"Metric with id {entity.ref_id} does not exist")
        await upsert_events(self._connection, self._metric_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Metric:
        """Find a metric by id."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[Metric]:
        """Find all metrics matching some criteria."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.metric_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._metric_table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[Metric]:
        """Find all big plans with generic filters."""
        query_stmt = select(self._metric_table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._metric_table.c.archived.is_(False))

        query_stmt = compile_query_relative_to(query_stmt, self._metric_table, kwargs)

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> Metric:
        """Hard remove a metric - an irreversible operation."""
        query_stmt = select(self._metric_table).where(
            self._metric_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise MetricNotFoundError(f"Metric with id {ref_id} does not exist")
        await self._connection.execute(
            delete(self._metric_table).where(
                self._metric_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._metric_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> Metric:
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
                str(row["metric_collection_ref_id"]),
            ),
            name=MetricName.from_raw(row["name"]),
            icon=EntityIcon.from_safe(row["icon"]) if row["icon"] else None,
            collection_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(row["collection_period"]),
                eisen=Eisen.from_raw(row["collection_eisen"])
                if row["collection_eisen"]
                else None,
                difficulty=Difficulty.from_raw(row["collection_difficulty"])
                if row["collection_difficulty"]
                else None,
                actionable_from_day=RecurringTaskDueAtDay(
                    row["collection_actionable_from_day"],
                )
                if row["collection_actionable_from_day"] is not None
                else None,
                actionable_from_month=RecurringTaskDueAtMonth(
                    row["collection_actionable_from_month"],
                )
                if row["collection_actionable_from_month"] is not None
                else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(
                    row["collection_due_at_time"],
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
            if row["collection_period"] is not None
            else None,
            metric_unit=MetricUnit.from_raw(row["metric_unit"])
            if row["metric_unit"]
            else None,
        )


class SqliteMetricEntryRepository(MetricEntryRepository):
    """A repository of metric entries."""

    _connection: Final[AsyncConnection]
    _metric_entry_table: Final[Table]
    _metric_entry_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
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
                "metric_ref_id",
                ForeignKey("metric.ref_id"),
                index=True,
                nullable=False,
            ),
            Column("collection_time", DateTime, nullable=False),
            Column("value", Float, nullable=False),
            keep_existing=True,
        )
        self._metric_entry_event_table = build_event_table(
            self._metric_entry_table,
            metadata,
        )

    async def create(self, entity: MetricEntry) -> MetricEntry:
        """Create a metric entry."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
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
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(self._connection, self._metric_entry_event_table, entity)
        return entity

    async def save(self, entity: MetricEntry) -> MetricEntry:
        """Save a metric entry - it should already exist."""
        result = await self._connection.execute(
            update(self._metric_entry_table)
            .where(self._metric_entry_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                metric_ref_id=entity.metric_ref_id.as_int(),
                collection_time=entity.collection_time.to_db(),
                value=entity.value,
            ),
        )
        if result.rowcount == 0:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {entity.ref_id} does not exist",
            )
        await upsert_events(self._connection, self._metric_entry_event_table, entity)
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> MetricEntry:
        """Load a given metric entry."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[MetricEntry]:
        """Retrieve all metric entries for a given metric."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.metric_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.archived.is_(False),
            )
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.ref_id.in_(
                    fi.as_int() for fi in filter_ref_ids
                ),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[MetricEntry]:
        """Find all big plans with generic filters."""
        query_stmt = select(self._metric_entry_table)
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._metric_entry_table.c.archived.is_(False)
            )

        query_stmt = compile_query_relative_to(
            query_stmt, self._metric_entry_table, kwargs
        )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> MetricEntry:
        """Hard remove a metric entry - an irreversible operation."""
        query_stmt = select(self._metric_entry_table).where(
            self._metric_entry_table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise MetricEntryNotFoundError(
                f"Metric entry with id {ref_id} does not exist",
            )
        await self._connection.execute(
            delete(self._metric_entry_table).where(
                self._metric_entry_table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._metric_entry_event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> MetricEntry:
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
            name=MetricEntry.build_name(
                ADate.from_db(row["collection_time"]), row["value"]
            ),
            metric_ref_id=EntityId.from_raw(str(row["metric_ref_id"])),
            collection_time=ADate.from_db(row["collection_time"]),
            value=row["value"],
        )
