"""A full day block in a schedule."""
from jupiter.core.domain.concept.schedule.schedule_event_name import ScheduleEventName
from jupiter.core.domain.concept.schedule.schedule_external_uid import (
    ScheduleExternalUid,
)
from jupiter.core.domain.concept.schedule.schedule_source import ScheduleSource
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
    source: ScheduleSource
    name: ScheduleEventName
    external_uid: ScheduleExternalUid | None

    time_event_full_days_block = OwnsOne(
        TimeEventFullDaysBlock,
        namespace=TimeEventNamespace.SCHEDULE_FULL_DAYS_BLOCK,
        source_entity_ref_id=IsRefId(),
    )
    note = OwnsAtMostOne(
        Note, domain=NoteDomain.SCHEDULE_EVENT_FULL_DAYS, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_schedule_full_days_block_for_user(
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
            source=ScheduleSource.USER,
            name=name,
            external_uid=None,
        )

    @staticmethod
    @create_entity_action
    def new_schedule_full_days_block_from_external_ical(
        ctx: DomainContext,
        schedule_domain_ref_id: EntityId,
        schedule_stream_ref_id: EntityId,
        name: ScheduleEventName,
        external_uid: ScheduleExternalUid,
    ) -> "ScheduleEventFullDays":
        """Create a schedule event from an external iCal."""
        return ScheduleEventFullDays._create(
            ctx,
            schedule_domain=ParentLink(schedule_domain_ref_id),
            schedule_stream_ref_id=schedule_stream_ref_id,
            source=ScheduleSource.EXTERNAL_ICAL,
            name=name,
            external_uid=external_uid,
        )

    @update_entity_action
    def change_schedule_stream(
        self,
        ctx: DomainContext,
        schedule_stream_ref_id: EntityId,
    ) -> "ScheduleEventFullDays":
        """Change the schedule stream."""
        if self.source == ScheduleSource.EXTERNAL_ICAL:
            raise Exception("Cannot change schedule stream for external iCal event.")
        return self._new_version(
            ctx,
            schedule_stream_ref_id=schedule_stream_ref_id,
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

    @property
    def can_be_modified_independently(self) -> bool:
        """Return whether the event can be modified independently."""
        return self.source == ScheduleSource.USER
