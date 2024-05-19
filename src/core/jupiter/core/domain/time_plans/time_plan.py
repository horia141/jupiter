"""A plan for a particular period of time."""
import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.core.timeline import infer_timeline
from jupiter.core.domain.time_plans.time_plan_activity import TimePlanActivity
from jupiter.core.domain.time_plans.time_plan_source import TimePlanSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    LeafEntity,
    OwnsOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    LeafEntityRepository,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class TimePlan(LeafEntity):
    """A plan for a particular period of time."""

    time_plan_domain: ParentLink

    source: TimePlanSource
    right_now: ADate
    period: RecurringTaskPeriod
    timeline: str

    activities = ContainsMany(TimePlanActivity, time_plan_ref_id=IsRefId())
    note = OwnsOne(Note, domain=NoteDomain.TIME_PLAN, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_time_plan_for_user(
        ctx: DomainContext,
        time_plan_domain_ref_id: EntityId,
        right_now: ADate,
        period: RecurringTaskPeriod,
    ) -> "TimePlan":
        """Create a time plan, as instructed by the user."""
        return TimePlan._create(
            ctx,
            name=TimePlan.build_name(right_now, period),
            time_plan_domain=ParentLink(time_plan_domain_ref_id),
            source=TimePlanSource.USER,
            right_now=right_now,
            period=period,
            timeline=infer_timeline(period, right_now.to_timestamp_at_end_of_day()),
        )

    @update_entity_action
    def change_time_config(
        self,
        ctx: DomainContext,
        right_now: UpdateAction[ADate],
        period: UpdateAction[RecurringTaskPeriod],
    ) -> "TimePlan":
        """Update the time plan."""
        return self._new_version(
            ctx,
            name=TimePlan.build_name(
                right_now.or_else(self.right_now), period.or_else(self.period)
            ),
            right_now=right_now.or_else(self.right_now),
            period=period.or_else(self.period),
            timeline=infer_timeline(
                period.or_else(self.period),
                right_now.or_else(self.right_now).to_timestamp_at_end_of_day(),
            ),
        )

    @staticmethod
    def build_name(right_now: ADate, period: RecurringTaskPeriod) -> EntityName:
        """Build the name of the time plan."""
        return EntityName(f"{period.value.capitalize()} plan for {right_now}")


class TimePlanExistsForDatePeriodCombinationError(EntityAlreadyExistsError):
    """An error raised when a time plan already exists for a date and period combination."""


class TimePlanRepository(LeafEntityRepository[TimePlan], abc.ABC):
    """The repository for time plans."""

    @abc.abstractmethod
    async def find_all_in_range(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        filter_periods: list[RecurringTaskPeriod],
        filter_start_date: ADate,
        filter_end_date: ADate,
    ) -> list[TimePlan]:
        """Find all time plans in a range."""

    @abc.abstractmethod
    async def find_previous(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool,
        period: RecurringTaskPeriod,
        right_now: ADate,
    ) -> TimePlan | None:
        """Find the previous time plan to a given right now at a certain period."""
