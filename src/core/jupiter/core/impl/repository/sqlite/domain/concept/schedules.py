"""SQLite implementation of schedules infra classes."""

from jupiter.core.domain.concept.schedule.schedule_external_sync_log_entry import (
    ScheduleExternalSyncLogEntry,
    ScheduleExternalSyncLogEntryRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteScheduleExternalSyncLogEntryRepository(
    SqliteLeafEntityRepository[ScheduleExternalSyncLogEntry],
    ScheduleExternalSyncLogEntryRepository,
):
    """SQLite implementation of the schedule external sync log entry repository."""

    async def find_last(
        self, parent_ref_id: EntityId, limit: int
    ) -> list[ScheduleExternalSyncLogEntry]:
        """Find the last N schedule external sync log entries."""
        if limit < 0:
            raise InputValidationError("Limit must be non-negative")
        if limit > 1000:
            raise InputValidationError("Limit must be less than or equal to 1000")
        query_stmt = (
            select(self._table)
            .where(
                self._table.c.schedule_external_sync_log_ref_id
                == parent_ref_id.as_int()
            )
            .order_by(self._table.c.created_time.desc())
            .limit(limit)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]
