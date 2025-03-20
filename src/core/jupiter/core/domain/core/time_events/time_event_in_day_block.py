"""Time event."""

import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafSupportEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.value import CompositeValue, value

# Define constants at the top level
MIN_DURATION_MINS = 1
MAX_DURATION_MINS = 2 * 24 * 60  # 48 hours


@entity
class TimeEventInDayBlock(LeafSupportEntity):
    """Time event."""

    time_event_domain: ParentLink

    namespace: TimeEventNamespace
    source_entity_ref_id: EntityId
    start_date: ADate
    start_time_in_day: TimeInDay
    duration_mins: int

    @staticmethod
    @create_entity_action
    def new_time_event_for_schedule_event(
        ctx: DomainContext,
        time_event_domain_ref_id: EntityId,
        schedule_event_ref_id: EntityId,
        start_date: ADate,
        start_time_in_day: TimeInDay,
        duration_mins: int,
    ) -> "TimeEventInDayBlock":
        """Create a new time event."""
        if duration_mins < MIN_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at least {MIN_DURATION_MINS} minute."
            )
        if duration_mins > MAX_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at most {MAX_DURATION_MINS // 60} hours."
            )
        return TimeEventInDayBlock._create(
            ctx,
            time_event_domain=ParentLink(time_event_domain_ref_id),
            namespace=TimeEventNamespace.SCHEDULE_EVENT_IN_DAY,
            source_entity_ref_id=schedule_event_ref_id,
            name=NOT_USED_NAME,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
        )

    @staticmethod
    @create_entity_action
    def new_time_event_for_inbox_task(
        ctx: DomainContext,
        time_event_domain_ref_id: EntityId,
        inbox_task_ref_id: EntityId,
        start_date: ADate,
        start_time_in_day: TimeInDay,
        duration_mins: int,
    ) -> "TimeEventInDayBlock":
        """Create a new time event."""
        if duration_mins < MIN_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at least {MIN_DURATION_MINS} minute."
            )
        if duration_mins > MAX_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at most {MAX_DURATION_MINS // 60} hours."
            )
        return TimeEventInDayBlock._create(
            ctx,
            time_event_domain=ParentLink(time_event_domain_ref_id),
            namespace=TimeEventNamespace.INBOX_TASK,
            source_entity_ref_id=inbox_task_ref_id,
            name=NOT_USED_NAME,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        start_date: UpdateAction[ADate],
        start_time_in_day: UpdateAction[TimeInDay],
        duration_mins: UpdateAction[int],
    ) -> "TimeEventInDayBlock":
        """Update the time event."""
        if duration_mins.test(lambda t: t < MIN_DURATION_MINS):
            raise InputValidationError(
                f"Duration must be at least {MIN_DURATION_MINS} minute."
            )
        if duration_mins.test(lambda t: t > MAX_DURATION_MINS):
            raise InputValidationError(
                f"Duration must be at most {MAX_DURATION_MINS // 60} hours."
            )
        return self._new_version(
            ctx,
            start_date=start_date.or_else(self.start_date),
            start_time_in_day=start_time_in_day.or_else(self.start_time_in_day),
            duration_mins=duration_mins.or_else(self.duration_mins),
        )

    @property
    def can_be_modified_independently(self) -> bool:
        """Check if the time event can be archived independently."""
        if self.namespace == TimeEventNamespace.INBOX_TASK:
            return True
        return False


@value
class TimeEventInDayBlockStatsPerGroup(CompositeValue):
    """Just a slice of the stats."""

    date: ADate
    namespace: TimeEventNamespace
    cnt: int


@value
class TimeEventInDayBlockStats(CompositeValue):
    """Stats for time events."""

    per_groups: list[TimeEventInDayBlockStatsPerGroup]


class TimeEventInDayBlockRepository(LeafEntityRepository[TimeEventInDayBlock], abc.ABC):
    """Time event repository."""

    @abc.abstractmethod
    async def load_for_namespace(
        self,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> TimeEventInDayBlock:
        """Load a time event for a namespace."""

    @abc.abstractmethod
    async def find_all_between(
        self,
        parent_ref_id: EntityId,
        start_date: ADate,
        end_date: ADate,
    ) -> list[TimeEventInDayBlock]:
        """Find all time events between two dates."""

    @abc.abstractmethod
    async def stats_for_all_between(
        self,
        parent_ref_id: EntityId,
        start_date: ADate,
        end_date: ADate,
    ) -> TimeEventInDayBlockStats:
        """Get stats for all time events between two dates."""
