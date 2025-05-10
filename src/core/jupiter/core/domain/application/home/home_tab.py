"""A tab on the home page."""

import abc
from typing import Literal
from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.application.home.widget import WidgetDimension, WidgetGeometry
from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    BranchEntity,
    ContainsMany,
    IsRefId,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.value import CompositeValue, value
from jupiter.core.domain.application.home.home_tab_widget_placement import OneOfHomeTabWidgetPlacement, build_home_tab_widget_placement

@entity
class HomeTab(BranchEntity):
    """A tab on the home page."""

    home_config: ParentLink
    target: HomeTabTarget
    name: EntityName
    icon: EntityIcon | None
    widget_placement: OneOfHomeTabWidgetPlacement

    widgets = ContainsMany(
        HomeWidget,
        home_tab_ref_id=IsRefId(),
    )

    @staticmethod
    @create_entity_action  
    def new_home_tab(
        ctx: DomainContext,
        home_config_ref_id: EntityId,
        target: HomeTabTarget,
        name: EntityName,
        icon: EntityIcon | None,
    ) -> "HomeTab":
        return HomeTab._create(
            ctx,
            home_config_ref_id=home_config_ref_id,
            target=target,
            name=name,
            icon=icon,
            widget_placement=build_home_tab_widget_placement(target),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[EntityName],
        icon: UpdateAction[EntityIcon | None],
    ) -> "HomeTab":
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
        )
    
    @update_entity_action
    def add_widget(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "HomeTab":
        widget_placement = self.widget_placement.add_widget(widget_ref_id, geometry)
        return self._new_version(ctx, widget_placement=widget_placement)

    @update_entity_action
    def remove_widget(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
    ) -> "HomeTab":
        widget_placement = self.widget_placement.remove_widget(widget_ref_id)
        return self._new_version(ctx, widget_placement=widget_placement)

    @update_entity_action
    def move_widget_to(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
        geometry: WidgetGeometry,
    ) -> "HomeTab":
        widget_placement = self.widget_placement.move_widget_to(widget_ref_id, geometry)
        return self._new_version(ctx, widget_placement=widget_placement)
