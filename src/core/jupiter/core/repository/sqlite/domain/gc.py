"""SQLite implementation of garbage collection infra classes."""

from jupiter.core.domain.entity_summary import EntitySummary
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.domain.gc.infra.gc_log_entry_repository import (
    GCLogEntryRepository,
)
from jupiter.core.domain.gc.infra.gc_log_repository import (
    GCLogRepository,
)
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import ParentLink
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
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
    select,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteGCLogRepository(SqliteTrunkEntityRepository[GCLog], GCLogRepository):
    """The GC log repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    @staticmethod
    def _entity_to_row(entity: GCLog) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "workspace_ref_id": entity.workspace.as_int(),
        }

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
            workspace=ParentLink(EntityId.from_raw(str(row["workspace_ref_id"]))),
        )


class SqliteGCLogEntryRepository(
    SqliteLeafEntityRepository[GCLogEntry], GCLogEntryRepository
):
    """Sqlite implementation of the GC log entry repository."""

    def __init__(self, connection: AsyncConnection, metadata: MetaData) -> None:
        """Constructor."""
        super().__init__(
            connection,
            metadata,
            Table(
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
            ),
        )

    async def find_last(self, parent_ref_id: EntityId, limit: int) -> list[GCLogEntry]:
        """Find the last N GC log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._table)
            .where(self._table.c.gc_log_ref_id == parent_ref_id.as_int())
            .order_by(self._table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    @staticmethod
    def _entity_to_row(entity: GCLogEntry) -> RowType:
        return {
            "version": entity.version,
            "archived": entity.archived,
            "created_time": entity.created_time.to_db(),
            "last_modified_time": entity.last_modified_time.to_db(),
            "archived_time": entity.archived_time.to_db()
            if entity.archived_time
            else None,
            "gc_log_ref_id": entity.gc_log.as_int(),
            "source": entity.source.value,
            "gc_targets": [g.value for g in entity.gc_targets],
            "opened": entity.opened,
            "entity_records": [r.to_json() for r in entity.entity_records],
        }

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
            gc_log=ParentLink(EntityId.from_raw(str(row["gc_log_ref_id"]))),
            source=EventSource(row["source"]),
            gc_targets=[SyncTarget.from_raw(g) for g in row["gc_targets"]],
            opened=row["opened"],
            entity_records=[EntitySummary.from_json(r) for r in row["entity_records"]],
        )
