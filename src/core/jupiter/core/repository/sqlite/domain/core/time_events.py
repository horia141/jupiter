"""Sqltite implementation of the time events repository."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
    TimeEventInDayBlockRepository,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.repository.sqlite.infra.repository import SqliteLeafEntityRepository
from sqlalchemy import (
    select,
)
from sqlalchemy.sql import and_, or_


class SqliteTimeEventInDayBlockRepository(
    SqliteLeafEntityRepository[TimeEventInDayBlock], TimeEventInDayBlockRepository
):
    """A repository of time events in day blocks."""

    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> TimeEventInDayBlock:
        """Retrieve a time event in day block via its namespace."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.namespace == namespace.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Time event in day block with namespace {namespace} and source {source_entity_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    async def find_all_between(
        self, parent_ref_id: EntityId, start_date: ADate, end_date: ADate
    ) -> list[TimeEventInDayBlock]:
        """Find all time events in day blocks between two dates."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.archived.is_(False))
            .where(self._table.c.time_event_domain_ref_id == parent_ref_id.as_int())
            .where(self._table.c.start_date >= start_date.the_date)
            .where(self._table.c.start_date <= end_date.the_date)
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]


class SqliteTimeEventFullDaysBlockRepository(
    SqliteLeafEntityRepository[TimeEventFullDaysBlock], TimeEventFullDaysBlockRepository
):
    """A repository of time events in full day blocks."""

    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> TimeEventFullDaysBlock:
        """Retrieve a time event in full day block via its namespace."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.namespace == namespace.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Time event in full day block with namespace {namespace} and source {source_entity_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    async def find_all_between(
        self, parent_ref_id: EntityId, start_date: ADate, end_date: ADate
    ) -> list[TimeEventFullDaysBlock]:
        """Find all time events in full day blocks between two dates."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.archived.is_(False))
            .where(self._table.c.time_event_domain_ref_id == parent_ref_id.as_int())
            .where(
                or_(
                    and_(
                        self._table.c.start_date >= start_date.the_date,
                        self._table.c.start_date <= end_date.the_date,
                    ),
                    and_(
                        self._table.c.end_date >= start_date.the_date,
                        self._table.c.end_date <= end_date.the_date,
                    ),
                )
            )
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]
