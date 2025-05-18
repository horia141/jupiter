"""A widget on the home page."""

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.domain.application.home.widget import (
    WIDGET_CONSTRAINTS,
    WidgetDimension,
    WidgetGeometry,
    WidgetType,
)
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)


@entity
class HomeWidget(LeafEntity):
    """A widget on the home page."""

    home_tab: ParentLink
    the_type: WidgetType
    geometry: WidgetGeometry

    @staticmethod
    @create_entity_action
    def new_home_widget(
        ctx: DomainContext,
        home_tab_ref_id: EntityId,
        home_tab_target: HomeTabTarget,
        the_type: WidgetType,
        geometry: WidgetGeometry,
    ) -> "HomeWidget":
        constraints = WIDGET_CONSTRAINTS.get(the_type, None)
        if constraints is None:
            raise ValueError(f"Widget type {the_type} is not supported")
        if geometry.dimension not in constraints.allowed_dimensions:
            raise ValueError(
                f"Dimension {geometry.dimension} is not allowed for widget type {the_type}"
            )
        if home_tab_target not in constraints.for_tab_target:
            raise ValueError(
                f"Widget type {the_type} is not allowed for tab target {home_tab_target}"
            )
        return HomeWidget._create(
            ctx,
            home_tab=ParentLink(home_tab_ref_id),
            name=HomeWidget._build_name(home_tab_target, home_tab_ref_id),
            the_type=the_type,
            geometry=geometry,
        )

    @update_entity_action
    def move_and_resize(
        self,
        ctx: DomainContext,
        row: int,
        col: int,
        dimension: WidgetDimension,
    ) -> "HomeWidget":
        return self._new_version(
            ctx,
            geometry=WidgetGeometry(row=row, col=col, dimension=dimension),
        )

    @staticmethod
    def _build_name(
        home_tab_target: HomeTabTarget, home_tab_ref_id: EntityId
    ) -> EntityName:
        return EntityName(f"Widget on {home_tab_target.value} {home_tab_ref_id}")
