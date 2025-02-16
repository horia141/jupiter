"""The SQLite repository for inbox tasks."""
from collections.abc import Iterable

from jupiter.core.domain.concept.inbox_tasks.inbox_task import (
    InboxTask,
    InboxTaskRepository,
)
from jupiter.core.domain.concept.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.concept.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteInboxTaskRepository(
    SqliteLeafEntityRepository[InboxTask], InboxTaskRepository
):
    """The inbox task repository."""

    async def find_all_for_source_created_desc(
        self,
        parent_ref_id: EntityId,
        source: InboxTaskSource,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> list[InboxTask]:
        """Find all the inbox task for a source."""
        query_stmt = select(self._table).where(
            self._table.c.inbox_task_collection_ref_id == parent_ref_id.as_int(),
            self._table.c.source == source.value,
            self._table.c.source_entity_ref_id == source_entity_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        query_stmt = query_stmt.order_by(self._table.c.created_time.desc())
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_modified_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
        filter_sources: Iterable[InboxTaskSource] | None = None,
        filter_project_ref_ids: Iterable[EntityId] | None = None,
        filter_last_modified_time_start: ADate | None = None,
        filter_last_modified_time_end: ADate | None = None,
    ) -> list[InboxTask]:
        """Find all the inbox task."""
        query_stmt = select(self._table).where(
            self._table.c.inbox_task_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_(fi.as_int() for fi in filter_ref_ids),
            )
        if filter_sources is not None:
            query_stmt = query_stmt.where(
                self._table.c.source.in_(s.value for s in filter_sources),
            )
        if filter_project_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.project_ref_id.in_(
                    fi.as_int() for fi in filter_project_ref_ids
                ),
            )
        if filter_last_modified_time_start is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                >= self._realm_codec_registry.db_encode(
                    filter_last_modified_time_start
                ),
            )
        if filter_last_modified_time_end is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                < self._realm_codec_registry.db_encode(filter_last_modified_time_end),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_completed_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_start_completed_date: ADate,
        filter_end_completed_date: ADate,
        filter_include_sources: Iterable[InboxTaskSource],
        filter_exclude_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[InboxTask]:
        """Find all completed inbox tasks in a time range."""
        query_stmt = select(self._table).where(
            self._table.c.inbox_task_collection_ref_id == parent_ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))

        start_completed_time = (
            filter_start_completed_date.to_timestamp_at_start_of_day()
        )
        end_completed_time = filter_end_completed_date.to_timestamp_at_end_of_day()

        query_stmt = (
            query_stmt.where(
                self._table.c.status.in_(
                    s.value for s in InboxTaskStatus.all_completed_statuses()
                )
            )
            .where(self._table.c.source.in_(s.value for s in filter_include_sources))
            .where(self._table.c.completed_time.is_not(None))
            .where(self._table.c.completed_time >= start_completed_time.the_ts)
            .where(self._table.c.completed_time <= end_completed_time.the_ts)
        )

        if filter_exclude_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.not_in(
                    fi.as_int() for fi in filter_exclude_ref_ids
                ),
            )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]
