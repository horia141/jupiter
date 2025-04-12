"""Sqltite implementation of the time events repository."""

from typing import cast

from jupiter.core.domain.core.adate import ADate, ADateDatabaseDecoder
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
    TimeEventFullDaysBlockRepository,
    TimeEventFullDaysBlockStats,
    TimeEventFullDaysBlockStatsPerGroup,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
    TimeEventInDayBlockRepository,
    TimeEventInDayBlockStats,
    TimeEventInDayBlockStatsPerGroup,
)
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import EntityNotFoundError
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import func, select
from sqlalchemy.sql import and_, or_

_ADATE_DECODER = ADateDatabaseDecoder()


class SqliteTimeEventInDayBlockRepository(
    SqliteLeafEntityRepository[TimeEventInDayBlock], TimeEventInDayBlockRepository
):
    """A repository of time events in day blocks."""

    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason] = False,
    ) -> TimeEventInDayBlock:
        """Retrieve a time event in day block via its namespace."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.namespace == namespace.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )
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

    async def stats_for_all_between(
        self, parent_ref_id: EntityId, start_date: ADate, end_date: ADate
    ) -> TimeEventInDayBlockStats:
        """Calculate stats for all time events in day blocks between two dates."""
        query_stmt = (
            select(
                self._table.c.start_date,
                self._table.c.namespace,
                func.count().label("count"),
            )
            .group_by(self._table.c.start_date, self._table.c.namespace)
            .where(self._table.c.archived.is_(False))
            .where(self._table.c.time_event_domain_ref_id == parent_ref_id.as_int())
            .where(self._table.c.archived.is_(False))
            .where(self._table.c.time_event_domain_ref_id == parent_ref_id.as_int())
            .where(self._table.c.start_date >= start_date.the_date)
            .where(self._table.c.start_date <= end_date.the_date)
        )

        result = await self._connection.execute(query_stmt)
        per_groups = []
        for row in result:
            per_groups.append(
                TimeEventInDayBlockStatsPerGroup(
                    date=_ADATE_DECODER.decode(row.start_date),
                    namespace=TimeEventNamespace(row.namespace),
                    cnt=cast(int, row.count),
                )
            )
        return TimeEventInDayBlockStats(per_groups=per_groups)


class SqliteTimeEventFullDaysBlockRepository(
    SqliteLeafEntityRepository[TimeEventFullDaysBlock], TimeEventFullDaysBlockRepository
):
    """A repository of time events in full day blocks."""

    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason] = False,
    ) -> TimeEventFullDaysBlock:
        """Retrieve a time event in full day block via its namespace."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.namespace == namespace.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Time event in full day block with namespace {namespace} and source {source_entity_ref_id} does not exist"
            )
        return self._row_to_entity(result)

    async def find_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason] = False,
    ) -> list[TimeEventFullDaysBlock]:
        """Retrieve a time event in full day block via its namespace."""
        query_stmt = (
            select(self._table)
            .where(self._table.c.namespace == namespace.value)
            .where(self._table.c.source_entity_ref_id == source_entity_ref_id.as_int())
        )
        if isinstance(allow_archived, bool):
            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        elif isinstance(allow_archived, ArchivalReason):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (self._table.c.archival_reason == str(allow_archived.value))
            )
        elif isinstance(allow_archived, list):
            query_stmt = query_stmt.where(
                (self._table.c.archived.is_(False))
                | (
                    self._table.c.archival_reason.in_(
                        [str(reason.value) for reason in allow_archived]
                    )
                )
            )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

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
                    # Start date is in range
                    and_(
                        self._table.c.start_date >= start_date.the_date,
                        self._table.c.start_date <= end_date.the_date,
                    ),
                    # End date is in range
                    and_(
                        self._table.c.end_date >= start_date.the_date,
                        self._table.c.end_date <= end_date.the_date,
                    ),
                    # Start and end date span the range
                    and_(
                        self._table.c.start_date <= start_date.the_date,
                        self._table.c.end_date >= end_date.the_date,
                    ),
                )
            )
        )
        result = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in result]

    async def stats_for_all_between(
        self, parent_ref_id: EntityId, start_date: ADate, end_date: ADate
    ) -> TimeEventFullDaysBlockStats:
        """Calculate stats for all time events in day blocks between two dates."""
        query_stmt = (
            select(
                self._table.c.start_date,
                self._table.c.namespace,
                func.count().label("count"),
            )
            .group_by(self._table.c.start_date, self._table.c.namespace)
            .where(self._table.c.archived.is_(False))
            .where(self._table.c.time_event_domain_ref_id == parent_ref_id.as_int())
            .where(
                or_(
                    # Start date is in range
                    and_(
                        self._table.c.start_date >= start_date.the_date,
                        self._table.c.start_date <= end_date.the_date,
                    ),
                    # End date is in range
                    and_(
                        self._table.c.end_date >= start_date.the_date,
                        self._table.c.end_date <= end_date.the_date,
                    ),
                    # Start and end date span the range
                    and_(
                        self._table.c.start_date <= start_date.the_date,
                        self._table.c.end_date >= end_date.the_date,
                    ),
                )
            )
        )

        result = await self._connection.execute(query_stmt)
        per_groups = []
        for row in result:
            per_groups.append(
                TimeEventFullDaysBlockStatsPerGroup(
                    date=_ADATE_DECODER.decode(row.start_date),
                    namespace=TimeEventNamespace(row.namespace),
                    cnt=cast(int, row.count),
                )
            )
        return TimeEventFullDaysBlockStats(per_groups=per_groups)
