"""A container for all the group of various push integrations we have."""

from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsOne,
    IsRefId,
    TrunkEntity,
    create_entity_action,
    entity,
)


@entity
class PushIntegrationGroup(TrunkEntity):
    """A container for all the group of various push integrations we have."""

    workspace_ref_id: EntityId

    email_task_collection = ContainsOne(
        EmailTaskCollection, push_integration_group_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_push_integration_group(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "PushIntegrationGroup":
        """Create a habit collection."""
        return PushIntegrationGroup._create(
            ctx,
            workspace_ref_id=workspace_ref_id,
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent entity id."""
        return self.workspace_ref_id
