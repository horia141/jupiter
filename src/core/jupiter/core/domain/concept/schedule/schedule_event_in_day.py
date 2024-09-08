"""An event in a schedule."""
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
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
class ScheduleEventInDay(LeafEntity):
    """An event in a schedule."""

    schedule_domain: ParentLink

    schedule_stream_ref_id: EntityId
    name: ScheduleEventName

    time_event_in_day_block = OwnsOne(
        TimeEventInDayBlock,
        namespace=TimeEventNamespace.SCHEDULE_EVENT_IN_DAY,
        source_entity_ref_id=IsRefId(),
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.SCHEDULE_EVENT_IN_DAY, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_schedule_event_in_day(
        ctx: DomainContext,
        schedule_domain_ref_id: EntityId,
        schedule_stream_ref_id: EntityId,
        name: ScheduleEventName,
    ) -> "ScheduleEventInDay":
        """Create a schedule event."""
        return ScheduleEventInDay._create(
            ctx,
            schedule_domain=ParentLink(schedule_domain_ref_id),
            schedule_stream_ref_id=schedule_stream_ref_id,
            name=name,
        )

    @update_entity_action
    def change_schedule_stream(
        self,
        ctx: DomainContext,
        schedule_stream_ref_id: EntityId,
    ) -> "ScheduleEventInDay":
        """Change the schedule stream."""
        return self._new_version(
            ctx,
            schedule_stream_ref_id=schedule_stream_ref_id,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[ScheduleEventName],
    ) -> "ScheduleEventInDay":
        """Update the schedule event."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )
