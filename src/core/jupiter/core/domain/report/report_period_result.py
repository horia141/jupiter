"""The result of a report."""
from dataclasses import field
from typing import Optional

from jupiter.core.domain.big_plans.big_plan_name import BigPlanName
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.recurring_task_period import RecurringTaskPeriod
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.value import Value, value


@value
class NestedResultPerSource(Value):
    """A particular result broken down by the various sources of inbox tasks."""

    source: InboxTaskSource
    count: int


@value
class NestedResult(Value):
    """A result broken down by the various sources of inbox tasks."""

    total_cnt: int
    per_source_cnt: list[NestedResultPerSource]


@value
class InboxTasksSummary(Value):
    """A bigger summary for inbox tasks."""

    created: NestedResult
    accepted: NestedResult
    working: NestedResult
    not_done: NestedResult
    done: NestedResult


@value
class WorkableBigPlan(Value):
    """The view of a big plan via a workable."""

    ref_id: EntityId
    name: BigPlanName
    actionable_date: Optional[ADate] = None


@value
class WorkableSummary(Value):
    """The reporting summary."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    done_cnt: int
    not_done_big_plans: list[WorkableBigPlan]
    done_big_plans: list[WorkableBigPlan]


@value
class BigPlanWorkSummary(Value):
    """The report for a big plan."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float


@value
class RecurringTaskWorkSummary(Value):
    """The reporting summary."""

    created_cnt: int
    accepted_cnt: int
    working_cnt: int
    not_done_cnt: int
    not_done_ratio: float
    done_cnt: int
    done_ratio: float
    streak_plot: str = field(hash=False, compare=False, repr=False, default="")


@value
class PerChoreBreakdownItem(Value):
    """The report for a particular chore."""

    ref_id: EntityId
    name: EntityName
    suspended: bool
    archived: bool
    period: RecurringTaskPeriod
    summary: RecurringTaskWorkSummary


@value
class PerHabitBreakdownItem(Value):
    """The report for a particular habit."""

    ref_id: EntityId
    name: EntityName
    archived: bool
    period: RecurringTaskPeriod
    suspended: bool
    summary: RecurringTaskWorkSummary


@value
class PerBigPlanBreakdownItem(Value):
    """The report for a particular big plan."""

    ref_id: EntityId
    name: EntityName
    actionable_date: Optional[ADate]
    summary: BigPlanWorkSummary


@value
class PerPeriodBreakdownItem(Value):
    """The report for a particular time period."""

    name: EntityName
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@value
class PerProjectBreakdownItem(Value):
    """The report for a particular project."""

    ref_id: EntityId
    name: EntityName
    inbox_tasks_summary: InboxTasksSummary
    big_plans_summary: WorkableSummary


@value
class ReportPeriodResult(Value):
    """Report result."""

    today: ADate
    period: RecurringTaskPeriod
    global_inbox_tasks_summary: InboxTasksSummary
    global_big_plans_summary: WorkableSummary
    per_project_breakdown: list[PerProjectBreakdownItem]
    per_period_breakdown: list[PerPeriodBreakdownItem]
    per_habit_breakdown: list[PerHabitBreakdownItem]
    per_chore_breakdown: list[PerChoreBreakdownItem]
    per_big_plan_breakdown: list[PerBigPlanBreakdownItem]
    user_score_overview: UserScoreOverview | None

    @staticmethod
    def empty(today: ADate, period: RecurringTaskPeriod) -> "ReportPeriodResult":
        """Construct an empty report."""
        return ReportPeriodResult(
            today=today,
            period=period,
            global_inbox_tasks_summary=InboxTasksSummary(
                created=NestedResult(
                    total_cnt=0,
                    per_source_cnt=[
                        NestedResultPerSource(source=s, count=0)
                        for s in InboxTaskSource
                    ],
                ),
                accepted=NestedResult(
                    total_cnt=0,
                    per_source_cnt=[
                        NestedResultPerSource(source=s, count=0)
                        for s in InboxTaskSource
                    ],
                ),
                working=NestedResult(
                    total_cnt=0,
                    per_source_cnt=[
                        NestedResultPerSource(source=s, count=0)
                        for s in InboxTaskSource
                    ],
                ),
                not_done=NestedResult(
                    total_cnt=0,
                    per_source_cnt=[
                        NestedResultPerSource(source=s, count=0)
                        for s in InboxTaskSource
                    ],
                ),
                done=NestedResult(
                    total_cnt=0,
                    per_source_cnt=[
                        NestedResultPerSource(source=s, count=0)
                        for s in InboxTaskSource
                    ],
                ),
            ),
            global_big_plans_summary=WorkableSummary(
                created_cnt=0,
                accepted_cnt=0,
                working_cnt=0,
                not_done_cnt=0,
                done_cnt=0,
                not_done_big_plans=[],
                done_big_plans=[],
            ),
            per_project_breakdown=[],
            per_period_breakdown=[],
            per_habit_breakdown=[],
            per_chore_breakdown=[],
            per_big_plan_breakdown=[],
            user_score_overview=None,
        )
