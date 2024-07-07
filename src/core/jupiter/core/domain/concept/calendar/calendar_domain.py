"""The calendar domain."""
from jupiter.core.domain.concept.calendar.calendar_event_full_days import CalendarEventFullDays
from jupiter.core.domain.concept.calendar.calendar_event_in_day import CalendarEventInDay
from jupiter.core.domain.concept.calendar.calendar_stream import CalendarStream
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class CalendarDomain(TrunkEntity):
    """The calendar domain."""

    workspace: ParentLink

    calendars = ContainsMany(CalendarStream, calendar_domain_ref_id=IsRefId())
    in_day_events = ContainsMany(CalendarEventInDay, calendar_domain_ref_id=IsRefId())
    full_days_events = ContainsMany(
        CalendarEventFullDays, calendar_domain_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_calendar_domain(
        ctx: DomainContext, workspace_ref_id: EntityId
    ) -> "CalendarDomain":
        """Create a new calendar domain."""
        return CalendarDomain._create(ctx, workspace=ParentLink(workspace_ref_id))
