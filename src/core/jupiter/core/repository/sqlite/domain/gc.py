"""SQLite implementation of garbage collection infra classes."""
from typing import Final, Iterable, List, Optional

from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.domain.gc.infra.gc_log_entry_repository import (
    GCLogEntryNotFoundError,
    GCLogEntryRepository,
)
from jupiter.core.domain.gc.infra.gc_log_repository import (
    GCLogAlreadyExistsError,
    GCLogNotFoundError,
    GCLogRepository,
)
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteGCLogRepository(GCLogRepository):
    """The GC log repository."""

    _connection: Final[AsyncConnection]
    _gc_log_table: Final[Table]
    _gc_log_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._gc_log_table = Table(
            "gc_log",
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
            keep_existing=True,
        )
        self._gc_log_event_table = build_event_table(
            self._gc_log_table,
            metadata,
        )

    async def create(self, entity: GCLog) -> GCLog:
        """Create a gc log."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._gc_log_table).values(
                    **ref_id_kw,
                    version=entity.version,
                    archived=entity.archived,
                    created_time=entity.created_time.to_db(),
                    last_modified_time=entity.last_modified_time.to_db(),
                    archived_time=entity.archived_time.to_db()
                    if entity.archived_time
                    else None,
                    workspace_ref_id=entity.workspace_ref_id.as_int(),
                ),
            )
        except IntegrityError as err:
            raise GCLogAlreadyExistsError(
                f"GC log for workspace {entity.workspace_ref_id} already exists",
            ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._gc_log_event_table,
            entity,
        )
        return entity

    async def save(self, entity: GCLog) -> GCLog:
        """Save a GC log."""
        result = await self._connection.execute(
            update(self._gc_log_table)
            .where(self._gc_log_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                workspace_ref_id=entity.workspace_ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise GCLogNotFoundError("The GC log does not exist")
        await upsert_events(
            self._connection,
            self._gc_log_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> GCLog:
        """Retrieve a GC log."""
        query_stmt = select(self._gc_log_table).where(
            self._gc_log_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gc_log_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GCLogNotFoundError(
                f"GC log with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def load_by_parent(self, parent_ref_id: EntityId) -> GCLog:
        """Retrieve a gc log for a project."""
        query_stmt = select(self._gc_log_table).where(
            self._gc_log_table.c.workspace_ref_id == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GCLogNotFoundError(
                f"GC log for user {parent_ref_id} does not exist",
            )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> GCLog:
        return GCLog(
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
        )


class SqliteGCLogEntryRepository(GCLogEntryRepository):
    """Sqlite implementation of the GC log entry repository."""

    _connection: Final[AsyncConnection]
    _gc_log_entry_table: Final[Table]
    _gc_log_entry_event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        self._connection = connection
        self._gc_log_entry_table = Table(
            "gc_log_entry",
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            Column(
                "gc_log_ref_id",
                Integer,
                ForeignKey("gc_log.ref_id"),
                nullable=False,
            ),
            Column("source", String, nullable=False),
            Column("gc_targets", JSON, nullable=False),
            Column("opened", Boolean, nullable=False),
            Column("entity_records", JSON, nullable=False),
            keep_existing=True,
        )
        self._gc_log_entry_event_table = build_event_table(
            self._gc_log_entry_table,
            metadata,
        )

    async def create(self, entity: GCLogEntry) -> GCLogEntry:
        """Create a GC log entry."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        result = await self._connection.execute(
            insert(self._gc_log_entry_table).values(
                **ref_id_kw,
                version=entity.version,
                archived=entity.archived,
                created_time=entity.created_time.to_db(),
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                gc_log_ref_id=entity.gc_log_ref_id.as_int(),
                source=entity.source.value,
                gc_targets=[g.value for g in entity.gc_targets],
                opened=entity.opened,
                entity_records=[r.to_json() for r in entity.entity_records],
            ),
        )
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._gc_log_entry_event_table,
            entity,
        )
        return entity

    async def save(self, entity: GCLogEntry) -> GCLogEntry:
        """Save the GC log entry."""
        result = await self._connection.execute(
            update(self._gc_log_entry_table)
            .where(self._gc_log_entry_table.c.ref_id == entity.ref_id.as_int())
            .values(
                version=entity.version,
                archived=entity.archived,
                last_modified_time=entity.last_modified_time.to_db(),
                archived_time=entity.archived_time.to_db()
                if entity.archived_time
                else None,
                gc_log_ref_id=entity.gc_log_ref_id.as_int(),
                source=entity.source.value,
                gc_targets=[g.value for g in entity.gc_targets],
                opened=entity.opened,
                entity_records=[r.to_json() for r in entity.entity_records],
            ),
        )
        if result.rowcount == 0:
            raise GCLogEntryNotFoundError(
                f"The GC log entry {entity.ref_id} does not exist"
            )
        await upsert_events(
            self._connection,
            self._gc_log_entry_event_table,
            entity,
        )
        return entity

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> GCLogEntry:
        """Retrieve a GC log entry."""
        query_stmt = select(self._gc_log_entry_table).where(
            self._gc_log_entry_table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gc_log_entry_table.c.archived.is_(False),
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise GCLogEntryNotFoundError(
                f"GC log entry with id {ref_id} does not exist",
            )
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[GCLogEntry]:
        """Find all GC log entries."""
        query_stmt = select(self._gc_log_entry_table).where(
            self._gc_log_entry_table.c.gc_log_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gc_log_entry_table.c.archived.is_(False),
            )
        if filter_ref_ids:
            query_stmt = query_stmt.where(
                self._gc_log_entry_table.c.ref_id.in_(
                    [ref_id.as_int() for ref_id in filter_ref_ids],
                ),
            )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[GCLogEntry]:
        """Find all big plans with generic filters."""
        query_stmt = select(self._gc_log_entry_table)
        if not allow_archived:
            query_stmt = query_stmt.where(
                self._gc_log_entry_table.c.archived.is_(False)
            )

        query_stmt = compile_query_relative_to(
            query_stmt, self._gc_log_entry_table, kwargs
        )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_last(self, parent_ref_id: EntityId, limit: int) -> list[GCLogEntry]:
        """Find the last N GC log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._gc_log_entry_table)
            .where(self._gc_log_entry_table.c.gc_log_ref_id == parent_ref_id.as_int())
            .order_by(self._gc_log_entry_table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def remove(self, ref_id: EntityId) -> GCLogEntry:
        """Remove a GC log entry."""
        result = await self._connection.execute(
            delete(self._gc_log_entry_table).where(
                self._gc_log_entry_table.c.ref_id == ref_id.as_int(),
            ),
        )
        if result.rowcount == 0:
            raise GCLogEntryNotFoundError(f"The GC log entry {ref_id} does not exist")
        await remove_events(
            self._connection,
            self._gc_log_entry_event_table,
            ref_id,
        )
        return self._row_to_entity(result)

    @staticmethod
    def _row_to_entity(row: RowType) -> GCLogEntry:
        return GCLogEntry(
            ref_id=EntityId.from_raw(str(row["ref_id"])),
            version=row["version"],
            archived=row["archived"],
            created_time=Timestamp.from_db(row["created_time"]),
            archived_time=Timestamp.from_db(row["archived_time"])
            if row["archived_time"]
            else None,
            last_modified_time=Timestamp.from_db(row["last_modified_time"]),
            events=[],
            name=GCLogEntry.build_name(
                [SyncTarget.from_raw(g) for g in row["gc_targets"]],
                Timestamp.from_db(row["created_time"]),
            ),
            gc_log_ref_id=EntityId.from_raw(str(row["gc_log_ref_id"])),
            source=EventSource(row["source"]),
            gc_targets=[SyncTarget.from_raw(g) for g in row["gc_targets"]],
            opened=row["opened"],
            entity_records=[EntitySummary.from_json(r) for r in row["entity_records"]],
        )
