"""Time event."""
from jupiter.core.domain.core.time_events.time_event_namespace import TimeEventNamespace
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError


@entity
class TimeEvent(LeafEntity):
    """Time event."""

    time_event_domain: ParentLink

    namespace: TimeEventNamespace
    source_entity_ref_id: EntityId
    start_time: Timestamp
    end_time: Timestamp

    @staticmethod
    @create_entity_action
    def new_time_event(
        ctx: DomainContext,
        time_event_domain_ref_id: EntityId,
        namespace: TimeEventNamespace,
        source_entity_ref_id: EntityId,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> "TimeEvent":
        """Create a new time event."""
        if start_time >= end_time:
            raise InputValidationError("Start time must be before end time.")
        return TimeEvent._create(
            ctx,
            time_event_domain=ParentLink(time_event_domain_ref_id),
            namespace=namespace,
            source_entity_ref_id=source_entity_ref_id,
            name=NOT_USED_NAME,
            start_time=start_time,
            end_time=end_time,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> "TimeEvent":
        """Update the time event."""
        if start_time >= end_time:
            raise InputValidationError("Start time must be before end time.")
        return self._new_version(
            ctx,
            start_time=start_time,
            end_time=end_time,
        )
