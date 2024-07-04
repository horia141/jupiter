"""The SQLite repository for big plans."""
from collections.abc import Iterable

from jupiter.core.domain.big_plans.big_plan import (
    BigPlan,
    BigPlanRepository,
)
from jupiter.core.domain.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    select,
)


class SqliteBigPlanRepository(SqliteLeafEntityRepository[BigPlan], BigPlanRepository):
    """The big plan repository."""

    async def find_completed_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_start_completed_date: ADate,
        filter_end_completed_date: ADate,
        filter_exclude_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[BigPlan]:
        """Find all completed big plans in a time range."""
        query_stmt = select(self._table).where(
            self._table.c.big_plan_collection_ref_id == parent_ref_id.as_int(),
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
                    s.value for s in BigPlanStatus.all_completed_statuses()
                )
            )
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
