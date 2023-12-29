"""A big plan collection."""

from jupiter.core.domain.big_plans.big_plan import BigPlan
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
class BigPlanCollection(TrunkEntity):
    """A big plan collection."""

    workspace: ParentLink

    big_plans = ContainsMany(BigPlan, big_plan_collection_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_big_plan_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "BigPlanCollection":
        """Create a big plan collection."""
        return BigPlanCollection._create(ctx, workspace=ParentLink(workspace_ref_id))
