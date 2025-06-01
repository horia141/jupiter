"""A type of widget."""

from jupiter.core.domain.application.home.home_tab_target import HomeTabTarget
from jupiter.core.framework.value import CompositeValue, EnumValue, enum_value, value


@enum_value
class WidgetDimension(EnumValue):
    """A dimension of a widget."""

    DIM_1x1 = "Dim-1x1"
    DIM_1x2 = "Dim-1x2"
    DIM_1x3 = "Dim-1x3"
    DIM_2x1 = "Dim-2x1"
    DIM_2x2 = "Dim-2x2"
    DIM_2x3 = "Dim-2x3"
    DIM_3x1 = "Dim-3x1"
    DIM_3x2 = "Dim-3x2"
    DIM_3x3 = "Dim-3x3"
    DIM_kx1 = "Dim-kx1"
    DIM_kx2 = "Dim-kx2"
    DIM_kx3 = "Dim-kx3"

    @property
    def rows(self) -> int:
        """The number of rows a widget of this dimension has."""
        return {
            WidgetDimension.DIM_1x1: 1,
            WidgetDimension.DIM_1x2: 1,
            WidgetDimension.DIM_1x3: 1,
            WidgetDimension.DIM_2x1: 2,
            WidgetDimension.DIM_2x2: 2,
            WidgetDimension.DIM_2x3: 2,
            WidgetDimension.DIM_3x1: 3,
            WidgetDimension.DIM_3x2: 3,
            WidgetDimension.DIM_3x3: 3,
            WidgetDimension.DIM_kx1: 1,
            WidgetDimension.DIM_kx2: 1,
            WidgetDimension.DIM_kx3: 1,
        }[self]

    @property
    def cols(self) -> int:
        """The number of columns a widget of this dimension has."""
        return {
            WidgetDimension.DIM_1x1: 1,
            WidgetDimension.DIM_1x2: 2,
            WidgetDimension.DIM_1x3: 3,
            WidgetDimension.DIM_2x1: 1,
            WidgetDimension.DIM_2x2: 2,
            WidgetDimension.DIM_2x3: 3,
            WidgetDimension.DIM_3x1: 1,
            WidgetDimension.DIM_3x2: 2,
            WidgetDimension.DIM_3x3: 3,
            WidgetDimension.DIM_kx1: 1,
            WidgetDimension.DIM_kx2: 2,
            WidgetDimension.DIM_kx3: 3,
        }[self]

    @property
    def is_k_sized(self) -> bool:
        """Whether the widget is k-sized."""
        return self in (
            WidgetDimension.DIM_kx1,
            WidgetDimension.DIM_kx2,
            WidgetDimension.DIM_kx3,
        )


@value
class WidgetGeometry(CompositeValue):
    """A geometry of a widget."""

    row: int
    col: int
    dimension: WidgetDimension

    def with_row(self, row: int) -> "WidgetGeometry":
        """Return a new geometry with the row changed."""
        return WidgetGeometry(row=row, col=self.col, dimension=self.dimension)


@enum_value
class WidgetType(EnumValue):
    """A type of widget."""

    MOTD = "motd"
    WORKING_MEMORY = "working-mem"
    KEY_HABITS_STREAKS = "key-habits-streaks"
    HABIT_INBOX_TASKS = "habit-inbox-tasks"
    CALENDAR_DAY = "calendar-day"
    SCHEDULE_DAY = "schedule-day"
    TIME_PLAN_VIEW = "time-plan-view"


@value
class WidgetTypeConstraints(CompositeValue):
    """A constraints for a widget type."""

    allowed_dimensions: dict[HomeTabTarget, list[WidgetDimension]]


WIDGET_CONSTRAINTS = {
    WidgetType.MOTD: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_1x1,
                WidgetDimension.DIM_1x2,
                WidgetDimension.DIM_1x3,
            ],
            HomeTabTarget.SMALL_SCREEN: [
                WidgetDimension.DIM_1x1,
            ],
        },
    ),
    WidgetType.WORKING_MEMORY: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [WidgetDimension.DIM_1x1],
            HomeTabTarget.SMALL_SCREEN: [WidgetDimension.DIM_1x1],
        },
    ),
    WidgetType.KEY_HABITS_STREAKS: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_1x1,
                WidgetDimension.DIM_1x2,
            ],
            HomeTabTarget.SMALL_SCREEN: [WidgetDimension.DIM_1x1],
        },
    ),
    WidgetType.HABIT_INBOX_TASKS: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
            HomeTabTarget.SMALL_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
        },
    ),
    WidgetType.CALENDAR_DAY: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
            HomeTabTarget.SMALL_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
        },
    ),
    WidgetType.SCHEDULE_DAY: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
            HomeTabTarget.SMALL_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
        },
    ),
    WidgetType.TIME_PLAN_VIEW: WidgetTypeConstraints(
        allowed_dimensions={
            HomeTabTarget.BIG_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
            HomeTabTarget.SMALL_SCREEN: [
                WidgetDimension.DIM_3x1,
                WidgetDimension.DIM_kx1,
            ],
        },
    ),
}
