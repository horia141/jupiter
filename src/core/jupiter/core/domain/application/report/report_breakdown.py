"""Options for the breakdowns in a report."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class ReportBreakdown(EnumValue):
    """Options for the breakdowns in a report."""

    GLOBAL = "global"
    PERIODS = "periods"
    PROJECTS = "projects"
    HABITS = "habits"
    CHORES = "chores"
    BIG_PLANS = "big-plans"
