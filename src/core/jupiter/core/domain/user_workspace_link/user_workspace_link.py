"""A 1:1 link between users and workspaces."""
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import RootEntity, create_entity_action, entity


@entity
class UserWorkspaceLink(RootEntity):
    """A 1:1 link between a user and a workspace."""

    user_ref_id: EntityId
    workspace_ref_id: EntityId

    @staticmethod
    @create_entity_action
    def new_user_workspace_link(
        ctx: DomainContext,
        user_ref_id: EntityId,
        workspace_ref_id: EntityId,
    ) -> "UserWorkspaceLink":
        """Create a new user workspace link."""
        return UserWorkspaceLink._create(
            ctx, user_ref_id=user_ref_id, workspace_ref_id=workspace_ref_id
        )
