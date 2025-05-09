"""A tab on the home page."""

from jupiter.core.domain.application.home.home_big_screen_widget import HomeBigScreenWidget
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
    TrunkEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


HOME_BIG_SCREEN_TAB_COLUMNS= 3


@entity
class HomeBigScreenTab(BranchEntity):
    """A tab on the home page."""

    home_config: ParentLink
    name: EntityName
    icon: EntityIcon | None

    placement_of_widgets: list[list[EntityId]]

    widgets = ContainsMany(
        HomeBigScreenWidget,
        home_big_screen_tab_ref_id=IsRefId(),
    )

    @staticmethod
    @create_entity_action
    def new_home_big_screen_tab(
        ctx: DomainContext,
        home_config_ref_id: EntityId,
        name: EntityName,
        icon: EntityIcon | None,
    ) -> "HomeBigScreenTab":
        return HomeBigScreenTab._create(
            ctx,
            home_config_ref_id=home_config_ref_id,
            name=name,
            icon=icon,
            placement_of_widgets=[[] for _ in range(HOME_BIG_SCREEN_TAB_COLUMNS)],
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[EntityName],
        icon: UpdateAction[EntityIcon | None],
    ) -> "HomeBigScreenTab":
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
        col: int,
        size: WidgetDimension,
    ) -> "HomeBigScreenTab":
        pass
        
    @update_entity_action
    def remove_widget(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
    ) -> "HomeBigScreenTab":
        pass

    @update_entity_action
    def move_widget_to(
        self,
        ctx: DomainContext,
        widget_ref_id: EntityId,
        row: int,
        col: int,
        size: WidgetDimension,
    ) -> "HomeBigScreenTab":
        pass
