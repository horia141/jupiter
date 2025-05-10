"""A tab on the home page."""

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.domain.application.home.home_widget import HomeWidget
from jupiter.core.domain.application.home.widget import WidgetDimension
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


@entity
class HomeTab(BranchEntity):
    """A tab on the home page."""

    home_config: ParentLink
    target: HomeTabTarget
    name: EntityName
    icon: EntityIcon | None
    placement_of_widgets: list[list[EntityId]]

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
            placement_of_widgets=[],
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
        row: int,
        dimension: WidgetDimension,
    ) -> "HomeTab":
        pass

    @update_entity_action
    def remove_widget(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
    ) -> "HomeTab":
        pass

    @update_entity_action
    def move_widget_to(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
        row: int,
        dimension: WidgetDimension,
    ) -> "HomeTab":
        pass
