"""A widget on the home page."""

from jupiter.core.domain.application.home.widget import WIDGET_CONSTRAINTS, WidgetDimension, WidgetType
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import LeafEntity, ParentLink, create_entity_action, entity


@entity
class HomeSmallScreenWidget(LeafEntity):
    """A widget on the home page."""

    home_small_screen_tab: ParentLink
    the_type: WidgetType
    dimension: WidgetDimension

    @staticmethod
    @create_entity_action
    def new_home_small_screen_widget(
        ctx: DomainContext,
        home_small_screen_tab_ref_id: EntityId,
        the_type: WidgetType,
        dimension: WidgetDimension,
    ) -> "HomeSmallScreenWidget":
        constraints = WIDGET_CONSTRAINTS.get(the_type, None)
        if constraints is None:
            raise ValueError(f"Widget type {the_type} is not supported")
        if dimension not in constraints.allowed_dimensions:
            raise ValueError(f"Dimension {dimension} is not allowed for widget type {the_type}")
        if not constraints.for_small_screen:
            raise ValueError(f"Widget type {the_type} is not allowed for small screen")
        return HomeSmallScreenWidget._create(
            ctx,
            home_small_screen_tab_ref_id=home_small_screen_tab_ref_id,
            the_type=the_type,
            dimension=dimension,
        )
