"""A type of widget."""

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.framework.value import CompositeValue, EnumValue, enum_value, value


@enum_value
class WidgetDimension(EnumValue):
    """A dimension of a widget."""

    DIM_1x1 = "1x1"
    DIM_1x2 = "1x2"
    DIM_1x3 = "1x3"
    DIM_2x1 = "2x1"
    DIM_2x2 = "2x2"
    DIM_2x3 = "2x3"
    DIM_3x1 = "3x1"
    DIM_3x2 = "3x2"
    DIM_3x3 = "3x3"
    DIM_kx1 = "kx1"
    DIM_kx2 = "kx2"
    DIM_kx3 = "kx3"


@enum_value
class WidgetType(EnumValue):
    """A type of widget."""

    MOTD = "motd"
    WORKING_MEMORY = "working-mem"
    KEY_HABITS_STREAKS = "key-habits-streaks"
    HABIT_INBOX_TASKS = "habit-inbox-tasks"
    CALENDAR_DAY = "calendar-day"


@value
class WidgetTypeConstraints(CompositeValue):
    """A constraints for a widget type."""

    allowed_dimensions: list[WidgetDimension]
    for_tab_target: set[HomeTabTarget]


WIDGET_CONSTRAINTS = {
    WidgetType.MOTD: WidgetTypeConstraints(
        allowed_dimensions=[
            WidgetDimension.DIM_1x1,
            WidgetDimension.DIM_1x2,
            WidgetDimension.DIM_1x3,
        ],
        for_tab_target={HomeTabTarget.BIG_SCREEN, HomeTabTarget.SMALL_SCREEN},
    ),
    WidgetType.WORKING_MEMORY: WidgetTypeConstraints(
        allowed_dimensions=[WidgetDimension.DIM_1x1],
        for_tab_target={HomeTabTarget.BIG_SCREEN, HomeTabTarget.SMALL_SCREEN},
    ),
    WidgetType.KEY_HABITS_STREAKS: WidgetTypeConstraints(
        allowed_dimensions=[WidgetDimension.DIM_1x1, WidgetDimension.DIM_1x2],
        for_tab_target={HomeTabTarget.BIG_SCREEN, HomeTabTarget.SMALL_SCREEN},
    ),
    WidgetType.HABIT_INBOX_TASKS: WidgetTypeConstraints(
        allowed_dimensions=[WidgetDimension.DIM_3x1, WidgetDimension.DIM_kx1],
        for_tab_target={HomeTabTarget.BIG_SCREEN, HomeTabTarget.SMALL_SCREEN},
    ),
    WidgetType.CALENDAR_DAY: WidgetTypeConstraints(
        allowed_dimensions=[WidgetDimension.DIM_3x1, WidgetDimension.DIM_kx1],
        for_tab_target={HomeTabTarget.BIG_SCREEN, HomeTabTarget.SMALL_SCREEN},
    ),
}
