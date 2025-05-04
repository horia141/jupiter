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
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.update_action import UpdateAction
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

    key_habits: list[EntityId]
    key_metrics: list[EntityId]

    desktop_config: HomeDesktopConfig
    mobile_config: HomeMobileConfig

    widgets = ContainsMany(HomeWidget, home_config_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_home_config(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
        key_habits: list[EntityId],
        key_metrics: list[EntityId],
    ) -> "HomeConfig":
        """Create a new home config."""
        if len(key_habits) > MAX_KEY_HABITS:
            raise InputValidationError(f"Too many key habits: {len(key_habits)}")
        if len(set(key_habits)) != len(key_habits):
            raise InputValidationError("Key habits must be unique")
        if len(key_metrics) > MAX_KEY_METRICS:
            raise InputValidationError(f"Too many key metrics: {len(key_metrics)}")
        if len(set(key_metrics)) != len(key_metrics):
            raise InputValidationError("Key metrics must be unique")

        return HomeConfig._create(
            ctx,
            workspace=ParentLink(workspace_ref_id),
            key_habits=key_habits,
            key_metrics=key_metrics,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        key_habits: UpdateAction[list[EntityId]],
        key_metrics: UpdateAction[list[EntityId]],
    ) -> "HomeConfig":
        """Update a home config."""
        if key_habits.test(lambda x: len(x) > MAX_KEY_HABITS):
            raise InputValidationError(
                f"Too many key habits: {len(key_habits.just_the_value)}"
            )
        if key_habits.test(lambda x: len(set(x)) != len(x)):
            raise InputValidationError("Key habits must be unique")
        if key_metrics.test(lambda x: len(x) > MAX_KEY_METRICS):
            raise InputValidationError(
                f"Too many key metrics: {len(key_metrics.just_the_value)}"
            )
        if key_metrics.test(lambda x: len(set(x)) != len(x)):
            raise InputValidationError("Key metrics must be unique")

        return self._new_version(
            ctx,
            key_habits=key_habits.or_else(self.key_habits),
            key_metrics=key_metrics.or_else(self.key_metrics),
        )
