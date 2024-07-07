"""A specific calendar group or stream of events."""
from jupiter.core.domain.concept.calendar.calendar_event_full_days import (
    CalendarEventFullDays,
)
from jupiter.core.domain.concept.calendar.calendar_event_in_day import (
    CalendarEventInDay,
)
from jupiter.core.domain.concept.calendar.calendar_stream_color import (
    CalendarStreamColor,
)
from jupiter.core.domain.concept.calendar.calendar_stream_name import CalendarStreamName
from jupiter.core.domain.concept.calendar.calendar_stream_source import (
    CalendarStreamSource,
)
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.url import URL
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


class CannotModifyCalendarStreamError(Exception):
    """Cannot modify the calendar stream."""


@entity
class CalendarStream(LeafEntity):
    """A calendar group or stream of events."""

    calendar_domain: ParentLink

    source: CalendarStreamSource
    name: CalendarStreamName
    color: CalendarStreamColor
    source_ical_url: URL | None

    in_day_events = OwnsMany(CalendarEventInDay, calendar_stream_ref_id=IsRefId())
    full_days_events = OwnsMany(CalendarEventFullDays, calendar_stream_ref_id=IsRefId())
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.CALENDAR_STREAM, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_calendar_stream_for_user(
        ctx: DomainContext,
        calendar_domain_ref_id: EntityId,
        name: CalendarStreamName,
        color: CalendarStreamColor,
    ) -> "CalendarStream":
        """Create a new calendar."""
        return CalendarStream._create(
            ctx,
            calendar_domain=ParentLink(calendar_domain_ref_id),
            source=CalendarStreamSource.USER,
            name=name,
            color=color,
            source_ical_url=None,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[CalendarStreamName],
        color: UpdateAction[CalendarStreamColor],
    ) -> "CalendarStream":
        """Update the calendar."""
        if self.source == CalendarStreamSource.EXTERNAL_ICAL:
            raise CannotModifyCalendarStreamError("Cannot modify an external calendar.")
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            color=color.or_else(self.color),
        )
