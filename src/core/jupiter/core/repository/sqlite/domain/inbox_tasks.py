"""The SQLite repository for inbox tasks."""
from typing import Iterable, List, Optional

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.core.domain.inbox_tasks.infra.inbox_task_repository import (
    InboxTaskRepository,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteInboxTaskCollectionRepository(
    SqliteTrunkEntityRepository[InboxTaskCollection], InboxTaskCollectionRepository
):
    """The inbox task collection repository."""


class SqliteInboxTaskRepository(
    SqliteLeafEntityRepository[InboxTask], InboxTaskRepository
):
    """The inbox task repository."""

    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_sources: Optional[Iterable[InboxTaskSource]] = None,
        filter_project_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_habit_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_chore_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_big_plan_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_journal_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_metric_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_person_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_slack_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_email_task_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_last_modified_time_start: Optional[ADate] = None,
        filter_last_modified_time_end: Optional[ADate] = None,
    ) -> List[InboxTask]:
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
        if filter_habit_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.habit_ref_id.in_(
                    fi.as_int() for fi in filter_habit_ref_ids
                ),
            )
        if filter_chore_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.chore_ref_id.in_(
                    fi.as_int() for fi in filter_chore_ref_ids
                ),
            )
        if filter_big_plan_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.big_plan_ref_id.in_(
                    fi.as_int() for fi in filter_big_plan_ref_ids
                ),
            )
        if filter_journal_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.journal_ref_id.in_(
                    fi.as_int() for fi in filter_journal_ref_ids
                ),
            )
        if filter_metric_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.metric_ref_id.in_(
                    fi.as_int() for fi in filter_metric_ref_ids
                ),
            )
        if filter_person_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.person_ref_id.in_(
                    fi.as_int() for fi in filter_person_ref_ids
                ),
            )
        if filter_slack_task_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.slack_task_ref_id.in_(
                    fi.as_int() for fi in filter_slack_task_ref_ids
                ),
            )
        if filter_email_task_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.email_task_ref_id.in_(
                    fi.as_int() for fi in filter_email_task_ref_ids
                ),
            )
        if filter_last_modified_time_start is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                >= self._realm_codec_registry.db_encode(filter_last_modified_time_start),
            )
        if filter_last_modified_time_end is not None:
            query_stmt = query_stmt.where(
                self._table.c.last_modified_time
                < self._realm_codec_registry.db_encode(filter_last_modified_time_end),
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]
