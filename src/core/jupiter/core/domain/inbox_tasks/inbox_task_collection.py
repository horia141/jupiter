"""A inbox task collection."""

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import TrunkEntity, create_entity_action, entity


@entity
class InboxTaskCollection(TrunkEntity):
    """A inbox task collection."""

    workspace_ref_id: EntityId

    @staticmethod
    @create_entity_action
    def new_inbox_task_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "InboxTaskCollection":
        """Create a inbox task collection."""
        return InboxTaskCollection._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
