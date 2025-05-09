"""The home config domain application."""

from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.value import CompositeValue, value

MAX_KEY_HABITS = 3
MAX_KEY_METRICS = 3

@value
class HomeDesktopTabConfig(CompositeValue):
    """A tab on the home page."""

    name: EntityName
    icon: EntityIcon | None
    widgets: list[list[EntityId]]


@value
class HomeDesktopConfig(CompositeValue):
    """A desktop config for the home page."""

    home_config: ParentLink
    tabs: list[HomeDesktopTabConfig]


@value
class HomeMobileTabConfig(CompositeValue):
    """A tab on the home page."""

    name: EntityName
    icon: EntityIcon | None
    widgets: list[list[EntityId]]


@value
class HomeMobileConfig(CompositeValue):
    """A mobile config for the home page."""

    home_config: ParentLink
    tabs: list[HomeMobileTabConfig]


@entity
class HomeConfig(TrunkEntity):
    """The home config entity."""

    workspace: ParentLink

    desktop_config: HomeDesktopConfig
    mobile_config: HomeMobileConfig

    widgets = ContainsMany(HomeWidget, home_config_ref_id=IsRefId())

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
