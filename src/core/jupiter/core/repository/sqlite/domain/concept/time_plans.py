"""The SQLite based time plans repository."""
from jupiter.core.domain.concept.time_plans.time_plan import (
    TimePlan,
    TimePlanExistsForDatePeriodCombinationError,
    TimePlanRepository,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity import (
    TimePlanActivity,
    TimePlanActivityRespository,
    TimePlanAlreadyAssociatedWithTargetError,
)
from jupiter.core.domain.concept.time_plans.time_plan_activity_target import (
    TimePlanActivityTarget,
)
from jupiter.core.domain.core import schedules
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteLeafEntityRepository,
)
from sqlalchemy import (
    MetaData,
)
from sqlalchemy.ext.asyncio import AsyncConnection


class SqliteTimePlanRepository(
    SqliteLeafEntityRepository[TimePlan], TimePlanRepository
):
    """A repository for time plans."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            already_exists_err_cls=TimePlanExistsForDatePeriodCombinationError,
        )

    async def find_all_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_periods: list[RecurringTaskPeriod],
        filter_start_date: ADate,
        filter_end_date: ADate,
    ) -> list[TimePlan]:
        """Find all time plans in a range."""
        if len(filter_periods) == 0:
            return []

        query_stmt = self._table.select().where(
            self._table.c.time_plan_domain_ref_id == parent_ref_id.as_int(),
        )

        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))

        query_stmt = query_stmt.where(
            self._table.c.period.in_([p.value for p in filter_periods])
        )
        query_stmt = query_stmt.where(
            self._table.c.right_now >= filter_start_date.the_date
        )
        query_stmt = query_stmt.where(
            self._table.c.right_now <= filter_end_date.the_date
        )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_higher(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        period: RecurringTaskPeriod,
        right_now: ADate,
    ) -> TimePlan | None:
        """Find the higher time plan to a given right now at a certain period."""
        for higher_period in period.all_higher_periods:
            query_stmt = self._table.select().where(
                self._table.c.time_plan_domain_ref_id == parent_ref_id.as_int(),
            )

            if not allow_archived:
                query_stmt = query_stmt.where(self._table.c.archived.is_(False))

            higher_schedule = schedules.get_schedule(
                higher_period,
                EntityName("Test"),
                right_now.to_timestamp_at_end_of_day(),
            )

            query_stmt = (
                query_stmt.where(self._table.c.period == higher_period.value)
                .where(self._table.c.timeline == higher_schedule.timeline)
                .order_by(self._table.c.right_now.desc())
                .limit(1)
            )

            result_rows = await self._connection.execute(query_stmt)
            results = [self._row_to_entity(row) for row in result_rows]
            if len(results) == 0:
                continue
            return results[0]

        return None

    async def find_previous(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        period: RecurringTaskPeriod,
        right_now: ADate,
    ) -> TimePlan | None:
        """Find the previous time plan to a given right now at a certain period."""
        query_stmt = self._table.select().where(
            self._table.c.time_plan_domain_ref_id == parent_ref_id.as_int(),
        )

        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))

        query_stmt = (
            query_stmt.where(self._table.c.period == period.value)
            .where(self._table.c.right_now < right_now.the_date)
            .order_by(self._table.c.right_now.desc())
            .limit(1)
        )

        result_rows = await self._connection.execute(query_stmt)
        results = [self._row_to_entity(row) for row in result_rows]
        if len(results) == 0:
            return None
        return results[0]


class SqliteTimePlanActivityRepository(
    SqliteLeafEntityRepository[TimePlanActivity], TimePlanActivityRespository
):
    """A repository for time plan activities."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry,
            connection,
            metadata,
            already_exists_err_cls=TimePlanAlreadyAssociatedWithTargetError,
        )

    async def find_all_with_target(
        self, target: TimePlanActivityTarget, target_ref_id: EntityId
    ) -> list[EntityId]:
        """Find all time plan activities with a target."""
        query_stmt = (
            self._table.select()
            .where(
                self._table.c.target == target.value,
            )
            .where(
                self._table.c.target_ref_id == target_ref_id.as_int(),
            )
            .where(
                self._table.c.archived.is_(False),
            )
        )

        results = await self._connection.execute(query_stmt)

        return [self._row_to_entity(row).parent_ref_id for row in results]
