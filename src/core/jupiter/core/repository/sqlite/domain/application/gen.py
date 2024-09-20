"""SQLite implementation of task generation infra classes."""

from jupiter.core.domain.application.gen.gen_log_entry import (
    GenLogEntry,
    GenLogEntryRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteGenLogEntryRepository(
    SqliteLeafEntityRepository[GenLogEntry], GenLogEntryRepository
):
    """Sqlite implementation of the task generation log entry repository."""

    async def find_last(self, parent_ref_id: EntityId, limit: int) -> list[GenLogEntry]:
        """Find the last N task generation log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._table)
            .where(self._table.c.gen_log_ref_id == parent_ref_id.as_int())
            .order_by(self._table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]
