"""The SQLite repository for big plans."""

from collections.abc import Iterable
from sqlite3 import IntegrityError
from typing import Final, Mapping, cast

from jupiter.core.domain.concept.big_plans.big_plan import (
    BigPlan,
    BigPlanRepository,
)
from jupiter.core.domain.concept.big_plans.big_plan_stats import (
    BigPlanStats,
    BigPlanStatsRepository,
)
from jupiter.core.domain.concept.big_plans.big_plan_status import BigPlanStatus
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.archival_reason import ArchivalReason
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.realm import RealmCodecRegistry, RealmThing
from jupiter.core.framework.repository import (
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from jupiter.core.impl.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
    SqliteRecordRepository,
)
from jupiter.core.impl.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteBigPlanRepository(SqliteLeafEntityRepository[BigPlan], BigPlanRepository):
    """The big plan repository."""

    async def find_completed_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool | ArchivalReason | list[ArchivalReason],
        filter_start_completed_date: ADate,
        filter_end_completed_date: ADate,
        filter_exclude_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[BigPlan]:
        """Find all completed big plans in a time range."""
        query_stmt = select(self._table).where(
            self._table.c.big_plan_collection_ref_id == parent_ref_id.as_int(),
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


class SqliteBigPlanStatsRepository(
    SqliteRecordRepository[BigPlanStats, EntityId], BigPlanStatsRepository
):
    """The big plan stats repository."""

    _big_plan_stats_table: Final[Table]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(realm_codec_registry, connection, metadata)
        self._big_plan_stats_table = Table(
            "big_plan_stats",
            metadata,
            Column(
                "big_plan_ref_id",
                Integer,
                ForeignKey("big_plan.ref_id"),
                nullable=False,
            ),
            Column("all_inbox_tasks_cnt", Integer, nullable=False),
            Column("completed_inbox_tasks_cnt", Integer, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            keep_existing=True,
        )

    async def create(self, record: BigPlanStats) -> BigPlanStats:
        """Create a new big plan stats."""
        try:
            await self._connection.execute(
                insert(self._big_plan_stats_table).values(
                    **(
                        cast(
                            Mapping[str, RealmThing],
                            self._realm_codec_registry.db_encode(record),
                        )
                    ),
                ),
            )
        except IntegrityError as err:
            raise RecordAlreadyExistsError(
                f"Big plan stats for big plan {record.big_plan.ref_id} already exists",
            ) from err
        return record

    async def save(self, record: BigPlanStats) -> BigPlanStats:
        """Save a big plan stats."""
        result = await self._connection.execute(
            update(self._big_plan_stats_table)
            .where(
                self._big_plan_stats_table.c.big_plan_ref_id == record.big_plan.as_int()
            )
            .values(
                **(
                    cast(
                        Mapping[str, RealmThing],
                        self._realm_codec_registry.db_encode(record),
                    )
                )
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats {record.big_plan.ref_id} does not exist"
            )
        return record

    async def remove(self, key: EntityId) -> None:
        """Remove a big plan stats."""
        result = await self._connection.execute(
            delete(self._big_plan_stats_table).where(
                self._big_plan_stats_table.c.big_plan_ref_id == key.as_int()
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats for big plan {key} does not exist"
            )

    async def load_by_key_optional(self, key: EntityId) -> BigPlanStats | None:
        """Load a big plan stats by it's unique key."""
        result = await self._connection.execute(
            select(self._big_plan_stats_table).where(
                self._big_plan_stats_table.c.big_plan_ref_id == key.as_int()
            )
        )
        result_x = result.first()
        if result_x is None:
            return None
        return self._row_to_entity(result_x)

    async def find_all(self, prefix: EntityId | list[EntityId]) -> list[BigPlanStats]:
        """Find all big plan stats for a big plan."""
        result = await self._connection.execute(
            select(self._big_plan_stats_table).where(
                self._big_plan_stats_table.c.big_plan_ref_id.in_(
                    [prefix.as_int()]
                    if isinstance(prefix, EntityId)
                    else [p.as_int() for p in prefix]
                )
            )
        )
        results = result.fetchall()
        return [self._row_to_entity(row) for row in results]

    async def mark_add_inbox_task(self, big_plan_ref_id: EntityId) -> None:
        """Mark that a new inbox task has been added to the big plan."""
        result = await self._connection.execute(
            update(self._big_plan_stats_table)
            .where(
                self._big_plan_stats_table.c.big_plan_ref_id == big_plan_ref_id.as_int()
            )
            .values(
                all_inbox_tasks_cnt=self._big_plan_stats_table.c.all_inbox_tasks_cnt + 1
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats {big_plan_ref_id} does not exist"
            )

    async def mark_remove_inbox_task(
        self, big_plan_ref_id: EntityId, is_completed: bool
    ) -> None:
        """Mark that an inbox task has been removed from the big plan."""
        query_stmt = (
            update(self._big_plan_stats_table)
            .where(
                self._big_plan_stats_table.c.big_plan_ref_id == big_plan_ref_id.as_int()
            )
            .where(self._big_plan_stats_table.c.all_inbox_tasks_cnt > 0)
        )
        if is_completed:
            query_stmt = query_stmt.values(
                completed_inbox_tasks_cnt=self._big_plan_stats_table.c.completed_inbox_tasks_cnt
                - 1,
                all_inbox_tasks_cnt=self._big_plan_stats_table.c.all_inbox_tasks_cnt
                - 1,
            )
        else:
            query_stmt = query_stmt.values(
                all_inbox_tasks_cnt=self._big_plan_stats_table.c.all_inbox_tasks_cnt - 1
            )
        result = await self._connection.execute(query_stmt)
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats {big_plan_ref_id} does not exist or has no tasks to remove"
            )

    async def mark_inbox_task_done(self, big_plan_ref_id: EntityId) -> None:
        """Mark that an inbox task has been done on the big plan."""
        result = await self._connection.execute(
            update(self._big_plan_stats_table)
            .where(
                self._big_plan_stats_table.c.big_plan_ref_id == big_plan_ref_id.as_int()
            )
            .where(
                self._big_plan_stats_table.c.completed_inbox_tasks_cnt
                < self._big_plan_stats_table.c.all_inbox_tasks_cnt
            )
            .values(
                completed_inbox_tasks_cnt=self._big_plan_stats_table.c.completed_inbox_tasks_cnt
                + 1
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats {big_plan_ref_id} does not exist"
            )

    async def mark_inbox_task_undone(self, big_plan_ref_id: EntityId) -> None:
        """Mark that an inbox task has been undone on the big plan."""
        result = await self._connection.execute(
            update(self._big_plan_stats_table)
            .where(
                self._big_plan_stats_table.c.big_plan_ref_id == big_plan_ref_id.as_int()
            )
            .where(self._big_plan_stats_table.c.completed_inbox_tasks_cnt > 0)
            .values(
                completed_inbox_tasks_cnt=self._big_plan_stats_table.c.completed_inbox_tasks_cnt
                - 1
            )
        )
        if result.rowcount == 0:
            raise RecordNotFoundError(
                f"The big plan stats {big_plan_ref_id} does not exist"
            )

    def _row_to_entity(self, row: RowType) -> BigPlanStats:
        return self._realm_codec_registry.db_decode(
            BigPlanStats, cast(Mapping[str, RealmThing], row._mapping)
        )
