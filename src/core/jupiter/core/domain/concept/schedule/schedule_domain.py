"""The schedule domain."""
from jupiter.core.domain.concept.schedule.schedule_event_full_days import (
    ScheduleEventFullDays,
)
from jupiter.core.domain.concept.schedule.schedule_event_in_day import (
    ScheduleEventInDay,
)
from jupiter.core.domain.concept.schedule.schedule_stream import ScheduleStream
from jupiter.core.domain.concept.schedule.schedule_sync_log import ScheduleSyncLog
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    ContainsOne,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class ScheduleDomain(TrunkEntity):
    """The schedule domain."""

    workspace: ParentLink

    sync_log = ContainsOne(ScheduleSyncLog, schedule_domain_ref_id=IsRefId())

    streams = ContainsMany(ScheduleStream, schedule_domain_ref_id=IsRefId())
    in_day_events = ContainsMany(ScheduleEventInDay, schedule_domain_ref_id=IsRefId())
    full_days_events = ContainsMany(
        ScheduleEventFullDays, schedule_domain_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_schedule_domain(
        ctx: DomainContext, workspace_ref_id: EntityId
    ) -> "ScheduleDomain":
        """Create a new schedule domain."""
        return ScheduleDomain._create(ctx, workspace=ParentLink(workspace_ref_id))
