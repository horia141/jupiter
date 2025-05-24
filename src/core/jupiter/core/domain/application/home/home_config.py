"""The home config domain application."""

from jupiter.core.domain.application.home.home_tab import HomeTab
from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.framework.base.entity_id import EntityId
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


@entity
class HomeConfig(TrunkEntity):
    """The home config entity."""

    workspace: ParentLink

    order_of_tabs: dict[HomeTabTarget, list[EntityId]]

    tabs = ContainsMany(HomeTab, home_config_ref_id=IsRefId())

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
            order_of_tabs={
                HomeTabTarget.BIG_SCREEN: [],
                HomeTabTarget.SMALL_SCREEN: [],
            },
        )

    @update_entity_action
    def add_tab(
        self,
        ctx: DomainContext,
        target: HomeTabTarget,
        tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(
            ctx,
            order_of_tabs={
                **self.order_of_tabs,
                target: [*self.order_of_tabs[target], tab_ref_id],
            },
        )

    @update_entity_action
    def remove_tab(
        self,
        ctx: DomainContext,
        target: HomeTabTarget,
        tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(
            ctx,
            order_of_tabs={
                **self.order_of_tabs,
                target: [
                    tab for tab in self.order_of_tabs[target] if tab != tab_ref_id
                ],
            },
        )

    @update_entity_action
    def reoder_tabs(
        self,
        ctx: DomainContext,
        target: HomeTabTarget,
        order_of_tabs: list[EntityId],
    ) -> "HomeConfig":
        return self._new_version(
            ctx, order_of_tabs={**self.order_of_tabs, target: order_of_tabs}
        )
