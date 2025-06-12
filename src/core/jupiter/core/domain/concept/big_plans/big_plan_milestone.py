"""A milestone for a big plan."""

from jupiter.core.domain.core.adate import ADate
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class BigPlanMilestone(LeafEntity):
    """A milestone for tracking progress of a big plan."""

    big_plan: ParentLink
    date: ADate
    description: str

    @staticmethod
    @create_entity_action
    def new_big_plan_milestone(
        ctx: DomainContext,
        big_plan_ref_id: EntityId,
        date: ADate,
        description: str,
    ) -> "BigPlanMilestone":
        """Create a big plan milestone."""
        return BigPlanMilestone._create(
            ctx,
            big_plan=ParentLink(big_plan_ref_id),
            date=date,
            description=description,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        date: UpdateAction[ADate],
        description: UpdateAction[str],
    ) -> "BigPlanMilestone":
        """Update the big plan milestone."""
        return self._new_version(
            ctx,
            date=date.or_else(self.date),
            description=description.or_else(self.description),
        )
