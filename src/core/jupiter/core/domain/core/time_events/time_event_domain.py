"""Time event domain trunk entity."""
from jupiter.core.domain.core.time_events.time_event_full_days_block import (
    TimeEventFullDaysBlock,
)
from jupiter.core.domain.core.time_events.time_event_in_day_block import (
    TimeEventInDayBlock,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    entity,
)


@entity
class TimeEventDomain(TrunkEntity):
    """Time event trunk entity."""

    workspace: ParentLink

    in_day_blocks = ContainsMany(
        TimeEventInDayBlock, time_event_domain_ref_id=IsRefId()
    )
    full_days_blocks = ContainsMany(
        TimeEventFullDaysBlock, time_event_domain_ref_id=IsRefId()
    )

    @staticmethod
    def new_time_event_domain(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "TimeEventDomain":
        """Create a inbox task collection."""
        return TimeEventDomain._create(ctx, workspace=ParentLink(workspace_ref_id))
