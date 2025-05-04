"""The home config domain application."""

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)

MAX_KEY_HABITS = 3
MAX_KEY_METRICS = 3


@entity
class HomeConfig(TrunkEntity):
    """The home config entity."""

    workspace: ParentLink

    @staticmethod
    @create_entity_action
    def new_home_config(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "HomeConfig":
        """Create a new home config."""
        return HomeConfig._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
    ) -> "HomeConfig":
        """Update a home config."""
        return self._new_version(
            ctx,
        )
