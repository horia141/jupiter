"""The home config domain application."""

from jupiter.core.domain.application.home.home_big_screen_tab import HomeBigScreenTab, HomeDesktopTab
from jupiter.core.domain.application.home.home_small_screen_tab import HomeMobileTab, HomeSmallScreenTab
from jupiter.core.domain.application.home.home_big_screen_widget import HomeWidget
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


@entity
class HomeConfig(TrunkEntity):
    """The home config entity."""

    workspace: ParentLink

    order_of_big_screen_tabs: list[EntityId]
    order_of_small_screen_tabs: list[EntityId]

    big_screen_tabs = ContainsMany(HomeBigScreenTab, home_config_ref_id=IsRefId())
    small_screen_tabs = ContainsMany(HomeSmallScreenTab, home_config_ref_id=IsRefId())
    
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
            order_of_big_screen_tabs=[],
            order_of_small_screen_tabs=[],
        )
    
    @update_entity_action
    def add_big_screen_tab(
        self,
        ctx: DomainContext,
        big_screen_tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_big_screen_tabs=[*self.order_of_big_screen_tabs, big_screen_tab_ref_id])  
    
    @update_entity_action
    def remove_big_screen_tab(
        self,
        ctx: DomainContext,
        big_screen_tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_big_screen_tabs=[*self.order_of_big_screen_tabs, big_screen_tab_ref_id])
    
    @update_entity_action
    def reorder_big_screen_tabs(
        self,
        ctx: DomainContext,
        order_of_big_screen_tabs: list[EntityId],
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_big_screen_tabs=order_of_big_screen_tabs)
    
    @update_entity_action
    def add_small_screen_tab(
        self,
        ctx: DomainContext,
        small_screen_tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_small_screen_tabs=[*self.order_of_small_screen_tabs, small_screen_tab_ref_id])
    
    @update_entity_action
    def remove_small_screen_tab(
        self,
        ctx: DomainContext,
        small_screen_tab_ref_id: EntityId,
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_small_screen_tabs=[*self.order_of_small_screen_tabs, small_screen_tab_ref_id])
    
    @update_entity_action
    def reorder_small_screen_tabs(
        self,
        ctx: DomainContext,
        order_of_small_screen_tabs: list[EntityId],
    ) -> "HomeConfig":
        return self._new_version(ctx, order_of_small_screen_tabs=order_of_small_screen_tabs)
