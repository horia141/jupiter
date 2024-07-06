"""The calendar domain."""
from jupiter.core.domain.calendar.calendar_event import CalendarEvent
from jupiter.core.domain.calendar.calendar_full_day_block import CalendarFullDayBlock
from jupiter.core.domain.calendar.calendar_stream import CalendarStream
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
    the_events = ContainsMany(CalendarEvent, calendar_domain_ref_id=IsRefId())
    full_day_blocks = ContainsMany(
        CalendarFullDayBlock, calendar_domain_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_calendar_domain(
        ctx: DomainContext, workspace_ref_id: EntityId
    ) -> "CalendarDomain":
        """Create a new calendar domain."""
        return CalendarDomain._create(ctx, workspace=ParentLink(workspace_ref_id))
