"""The time plan trunk domain object."""
from jupiter.core.domain.time_plans.time_plan import TimePlan
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
class TimePlanDomain(TrunkEntity):
    """A time plan trunk domain object."""

    workspace: ParentLink

    days_until_gc: int

    time_plans = ContainsMany(TimePlan, time_plan_domain_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_time_plan_domain(
        ctx: DomainContext, workspace_ref_id: EntityId, days_until_gc: int
    ) -> "TimePlanDomain":
        """Create a new time plan domain."""
        return TimePlanDomain._create(
            ctx, workspace=ParentLink(workspace_ref_id), days_until_gc=days_until_gc
        )
