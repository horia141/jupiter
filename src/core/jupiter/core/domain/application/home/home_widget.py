"""A widget on the home page."""

from jupiter.core.domain.application.home.widget import WidgetDimension, WidgetType
from jupiter.core.framework.entity import LeafEntity, ParentLink, entity


@entity
class HomeWidget(LeafEntity):
    """A widget on the home page."""

    home_config: ParentLink
    the_type: WidgetType
    dimension: WidgetDimension
