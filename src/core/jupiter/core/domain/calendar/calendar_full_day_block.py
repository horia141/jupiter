"""A full day block in a calendar."""
from jupiter.core.domain.calendar.calendar_full_day_block_name import (
    CalendarFullDayBlockName,
)
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event import TimeEvent
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    OwnsOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class CalendarFullDayBlock(LeafEntity):
    """A full day block in a calendar."""

    calendar_domain: ParentLink

    calendar_stream_ref_id: EntityId
    name: CalendarFullDayBlockName

    time_event = OwnsOne(
        TimeEvent,
        domain=TimeEventNamespace.CALENDAR_FULL_DAY_BLOCK,
        source_entity_ref_id=IsRefId(),
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.CALENDAR_FULL_DAY_BLOCK, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_calendar_full_day_block(
        ctx: DomainContext,
        calendar_domain_ref_id: EntityId,
        calendar_stream_ref_id: EntityId,
        name: CalendarFullDayBlockName,
    ) -> "CalendarFullDayBlock":
        """Create a calendar event."""
        return CalendarFullDayBlock._create(
            ctx,
            calendar_domain=ParentLink(calendar_domain_ref_id),
            calendar_stream_ref_id=calendar_stream_ref_id,
            name=name,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[CalendarFullDayBlockName],
    ) -> "CalendarFullDayBlock":
        """Update the calendar event."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )
