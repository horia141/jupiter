"""A full day block in a schedule."""
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
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
class ScheduleEventFullDays(LeafEntity):
    """A full day block in a schedule."""

    schedule_domain: ParentLink

    schedule_stream_ref_id: EntityId
    name: ScheduleEventName

    time_event_full_day_block = OwnsOne(
        TimeEventFullDaysBlock,
        namespace=TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
        source_entity_ref_id=IsRefId(),
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.SCHEDULE_EVENT_FULL_DAYS, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_schedule_full_days_block(
        ctx: DomainContext,
        schedule_domain_ref_id: EntityId,
        schedule_stream_ref_id: EntityId,
        name: ScheduleEventName,
    ) -> "ScheduleEventFullDays":
        """Create a schedule event."""
        return ScheduleEventFullDays._create(
            ctx,
            schedule_domain=ParentLink(schedule_domain_ref_id),
            schedule_stream_ref_id=schedule_stream_ref_id,
            name=name,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[ScheduleEventName],
    ) -> "ScheduleEventFullDays":
        """Update the schedule event."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
        )
