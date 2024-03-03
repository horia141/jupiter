"""SQLite implementation of garbage collection infra classes."""

from jupiter.core.domain.gc.gc_log_entry import (
    GCLogEntry,
    GCLogEntryRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteGCLogEntryRepository(
    SqliteLeafEntityRepository[GCLogEntry], GCLogEntryRepository
):
    """Sqlite implementation of the GC log entry repository."""

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
