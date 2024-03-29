"""A calendar event."""
from jupiter.core.domain.calendar.calendar_event_name import CalendarEventName
from jupiter.core.domain.calendar.calendar_event_source import CalendarEventSource
from jupiter.core.domain.calendar.calendar_event_type import CalendarEventType
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import IsRefId, LeafEntity, OwnsAtMostOne, ParentLink, create_entity_action, entity
from jupiter.core.framework.errors import InputValidationError


@entity
class CalendarEvent(LeafEntity):
    """A calendar event."""

    calendar: ParentLink
    source: CalendarEventSource
    name: CalendarEventName
    the_type: CalendarEventType
    start_date: ADate
    start_time: Timestamp | None
    end_date: ADate
    end_time: Timestamp | None

    note = OwnsAtMostOne(
        Note, domain=NoteDomain.CALENDAR_EVENT, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_calendar_event_for_user(
        ctx: DomainContext,
        calendar_ref_id: EntityId,
        name: CalendarEventName,
        the_type: CalendarEventType,
        start_date: ADate | None,
        start_time: Timestamp | None,
        end_date: ADate | None,
        end_time: Timestamp | None,
    ) -> "CalendarEvent":
        """Create a calendar event."""
        if the_type is CalendarEventType.MULTI_DAY:
            if start_time is not None:
                raise InputValidationError(
                    "Cannot set start_time for an all-day event"
                )
            if end_time is not None:
                raise InputValidationError("Cannot set end_time for an all-day event")
        elif the_type is CalendarEventType.INTRA_DAY:
            if start_date is not None:
                raise InputValidationError("Cannot set start_date for a time event")
            if start_time is None:
                raise InputValidationError(
                    "Must set start_time for a time-block event"
                )
            if end_date is not None:
                raise InputValidationError("Cannot set end_date for a time event")
            if end_time is None:
                raise InputValidationError(
                    "Must set end_time for a time-block event"
                )
            if start_time >= end_time:
                raise InputValidationError(
                    "Cannot set a start time after the end time"
                )

            start_date = ADate.from_timestamp(start_time)
            end_date = ADate.from_timestamp(end_time)

        if start_date is None:
            raise InputValidationError("Must set start_date for an event")
        if end_date is None:
            raise InputValidationError("Must set end_date for an event")
        if start_date > end_date:
            raise InputValidationError("Cannot set a start date after the end date")
        

        return CalendarEvent._create(
            ctx,
            calendar=ParentLink(calendar_ref_id),
            source=CalendarEventSource.USER,
            name=name,
            the_type=the_type,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
        )
    
    @staticmethod
    @create_entity_action
    def new_calendar_event_for_person_birthday(
        ctx: DomainContext,
        calendar_ref_id: EntityId,
        name: CalendarEventName,
        person_birthday: ADate,
    ) -> "CalendarEvent":
        """Create a calendar event."""
        return CalendarEvent._create(
            ctx,
            calendar=ParentLink(calendar_ref_id),
            source=CalendarEventSource.PERSON_BIRTHDAY,
            name=name,
            the_type=CalendarEventType.MULTI_DAY,
            start_date=person_birthday,
            start_time=None,
            end_date=person_birthday,
            end_time=None,
        )
    
    @staticmethod
    @create_entity_action
    def new_calendar_event_for_vacation(
        ctx: DomainContext,
        calendar_ref_id: EntityId,
        name: CalendarEventName,
        start_date: ADate,
        end_date: ADate,
    ) -> "CalendarEvent":
        """Create a calendar event."""
        if start_date >= end_date:
            raise InputValidationError("Cannot set a start date after the end date")
        return CalendarEvent._create(
            ctx,
            calendar=ParentLink(calendar_ref_id),
            source=CalendarEventSource.VACATION,
            name=name,
            the_type=CalendarEventType.MULTI_DAY,
            start_date=start_date,
            start_time=None,
            end_date=end_date,
            end_time=None,
        )
