"""Time event."""
import abc

from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.domain.core.time_in_day import TimeInDay
from jupiter.core.domain.core.timezone import Timezone
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
    timezone: Timezone

    @staticmethod
    @create_entity_action
    def new_time_event(
        ctx: DomainContext,
        time_event_domain_ref_id: EntityId,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        start_date: ADate,
        start_time_in_day: TimeInDay,
        duration_mins: int,
        timezone: Timezone,
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
            namespace=namespace,
            source_entity_ref_id=source_entity_ref_id,
            name=NOT_USED_NAME,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
            timezone=timezone,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        start_date: ADate,
        start_time_in_day: TimeInDay,
        duration_mins: int,
        timezone: Timezone,
    ) -> "TimeEventInDayBlock":
        """Update the time event."""
        if duration_mins < MIN_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at least {MIN_DURATION_MINS} minute."
            )
        if duration_mins > MAX_DURATION_MINS:
            raise InputValidationError(
                f"Duration must be at most {MAX_DURATION_MINS // 60} hours."
            )
        return self._new_version(
            ctx,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
            timezone=timezone,
        )


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
