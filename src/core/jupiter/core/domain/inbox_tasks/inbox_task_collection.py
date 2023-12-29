"""A inbox task collection."""

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class InboxTaskCollection(TrunkEntity):
    """A inbox task collection."""

    workspace: ParentLink

    @staticmethod
    @create_entity_action
    def new_inbox_task_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "InboxTaskCollection":
        """Create a inbox task collection."""
        return InboxTaskCollection._create(ctx, workspace=ParentLink(workspace_ref_id))
