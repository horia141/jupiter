from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inbox_task_source import InboxTaskSource
from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.report_breakdown import ReportBreakdown
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_tasks_summary import InboxTasksSummary
    from ..models.per_big_plan_breakdown_item import PerBigPlanBreakdownItem
    from ..models.per_chore_breakdown_item import PerChoreBreakdownItem
    from ..models.per_habit_breakdown_item import PerHabitBreakdownItem
    from ..models.per_period_breakdown_item import PerPeriodBreakdownItem
    from ..models.per_project_breakdown_item import PerProjectBreakdownItem
    from ..models.user_score_overview import UserScoreOverview
    from ..models.workable_summary import WorkableSummary


T = TypeVar("T", bound="ReportPeriodResult")


@_attrs_define
class ReportPeriodResult:
    """Report result.

    Attributes:
        today (str): A date or possibly a datetime for the application.
        period (RecurringTaskPeriod): A period for a particular task.
        sources (List[InboxTaskSource]):
        breakdowns (List[ReportBreakdown]):
        global_inbox_tasks_summary (InboxTasksSummary): A bigger summary for inbox tasks.
        global_big_plans_summary (WorkableSummary): The reporting summary.
        per_project_breakdown (List['PerProjectBreakdownItem']):
        per_period_breakdown (List['PerPeriodBreakdownItem']):
        per_habit_breakdown (List['PerHabitBreakdownItem']):
        per_chore_breakdown (List['PerChoreBreakdownItem']):
        per_big_plan_breakdown (List['PerBigPlanBreakdownItem']):
        breakdown_period (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
        user_score_overview (Union[Unset, UserScoreOverview]): An overview of the scores for a user.
    """

    today: str
    period: RecurringTaskPeriod
    sources: List[InboxTaskSource]
    breakdowns: List[ReportBreakdown]
    global_inbox_tasks_summary: "InboxTasksSummary"
    global_big_plans_summary: "WorkableSummary"
    per_project_breakdown: List["PerProjectBreakdownItem"]
    per_period_breakdown: List["PerPeriodBreakdownItem"]
    per_habit_breakdown: List["PerHabitBreakdownItem"]
    per_chore_breakdown: List["PerChoreBreakdownItem"]
    per_big_plan_breakdown: List["PerBigPlanBreakdownItem"]
    breakdown_period: Union[Unset, RecurringTaskPeriod] = UNSET
    user_score_overview: Union[Unset, "UserScoreOverview"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        today = self.today

        period = self.period.value

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.value
            sources.append(sources_item)

        breakdowns = []
        for breakdowns_item_data in self.breakdowns:
            breakdowns_item = breakdowns_item_data.value
            breakdowns.append(breakdowns_item)

        global_inbox_tasks_summary = self.global_inbox_tasks_summary.to_dict()

        global_big_plans_summary = self.global_big_plans_summary.to_dict()

        per_project_breakdown = []
        for per_project_breakdown_item_data in self.per_project_breakdown:
            per_project_breakdown_item = per_project_breakdown_item_data.to_dict()
            per_project_breakdown.append(per_project_breakdown_item)

        per_period_breakdown = []
        for per_period_breakdown_item_data in self.per_period_breakdown:
            per_period_breakdown_item = per_period_breakdown_item_data.to_dict()
            per_period_breakdown.append(per_period_breakdown_item)

        per_habit_breakdown = []
        for per_habit_breakdown_item_data in self.per_habit_breakdown:
            per_habit_breakdown_item = per_habit_breakdown_item_data.to_dict()
            per_habit_breakdown.append(per_habit_breakdown_item)

        per_chore_breakdown = []
        for per_chore_breakdown_item_data in self.per_chore_breakdown:
            per_chore_breakdown_item = per_chore_breakdown_item_data.to_dict()
            per_chore_breakdown.append(per_chore_breakdown_item)

        per_big_plan_breakdown = []
        for per_big_plan_breakdown_item_data in self.per_big_plan_breakdown:
            per_big_plan_breakdown_item = per_big_plan_breakdown_item_data.to_dict()
            per_big_plan_breakdown.append(per_big_plan_breakdown_item)

        breakdown_period: Union[Unset, str] = UNSET
        if not isinstance(self.breakdown_period, Unset):
            breakdown_period = self.breakdown_period.value

        user_score_overview: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_score_overview, Unset):
            user_score_overview = self.user_score_overview.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "today": today,
                "period": period,
                "sources": sources,
                "breakdowns": breakdowns,
                "global_inbox_tasks_summary": global_inbox_tasks_summary,
                "global_big_plans_summary": global_big_plans_summary,
                "per_project_breakdown": per_project_breakdown,
                "per_period_breakdown": per_period_breakdown,
                "per_habit_breakdown": per_habit_breakdown,
                "per_chore_breakdown": per_chore_breakdown,
                "per_big_plan_breakdown": per_big_plan_breakdown,
            }
        )
        if breakdown_period is not UNSET:
            field_dict["breakdown_period"] = breakdown_period
        if user_score_overview is not UNSET:
            field_dict["user_score_overview"] = user_score_overview

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_tasks_summary import InboxTasksSummary
        from ..models.per_big_plan_breakdown_item import PerBigPlanBreakdownItem
        from ..models.per_chore_breakdown_item import PerChoreBreakdownItem
        from ..models.per_habit_breakdown_item import PerHabitBreakdownItem
        from ..models.per_period_breakdown_item import PerPeriodBreakdownItem
        from ..models.per_project_breakdown_item import PerProjectBreakdownItem
        from ..models.user_score_overview import UserScoreOverview
        from ..models.workable_summary import WorkableSummary

        d = src_dict.copy()
        today = d.pop("today")

        period = RecurringTaskPeriod(d.pop("period"))

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = InboxTaskSource(sources_item_data)

            sources.append(sources_item)

        breakdowns = []
        _breakdowns = d.pop("breakdowns")
        for breakdowns_item_data in _breakdowns:
            breakdowns_item = ReportBreakdown(breakdowns_item_data)

            breakdowns.append(breakdowns_item)

        global_inbox_tasks_summary = InboxTasksSummary.from_dict(d.pop("global_inbox_tasks_summary"))

        global_big_plans_summary = WorkableSummary.from_dict(d.pop("global_big_plans_summary"))

        per_project_breakdown = []
        _per_project_breakdown = d.pop("per_project_breakdown")
        for per_project_breakdown_item_data in _per_project_breakdown:
            per_project_breakdown_item = PerProjectBreakdownItem.from_dict(per_project_breakdown_item_data)

            per_project_breakdown.append(per_project_breakdown_item)

        per_period_breakdown = []
        _per_period_breakdown = d.pop("per_period_breakdown")
        for per_period_breakdown_item_data in _per_period_breakdown:
            per_period_breakdown_item = PerPeriodBreakdownItem.from_dict(per_period_breakdown_item_data)

            per_period_breakdown.append(per_period_breakdown_item)

        per_habit_breakdown = []
        _per_habit_breakdown = d.pop("per_habit_breakdown")
        for per_habit_breakdown_item_data in _per_habit_breakdown:
            per_habit_breakdown_item = PerHabitBreakdownItem.from_dict(per_habit_breakdown_item_data)

            per_habit_breakdown.append(per_habit_breakdown_item)

        per_chore_breakdown = []
        _per_chore_breakdown = d.pop("per_chore_breakdown")
        for per_chore_breakdown_item_data in _per_chore_breakdown:
            per_chore_breakdown_item = PerChoreBreakdownItem.from_dict(per_chore_breakdown_item_data)

            per_chore_breakdown.append(per_chore_breakdown_item)

        per_big_plan_breakdown = []
        _per_big_plan_breakdown = d.pop("per_big_plan_breakdown")
        for per_big_plan_breakdown_item_data in _per_big_plan_breakdown:
            per_big_plan_breakdown_item = PerBigPlanBreakdownItem.from_dict(per_big_plan_breakdown_item_data)

            per_big_plan_breakdown.append(per_big_plan_breakdown_item)

        _breakdown_period = d.pop("breakdown_period", UNSET)
        breakdown_period: Union[Unset, RecurringTaskPeriod]
        if isinstance(_breakdown_period, Unset):
            breakdown_period = UNSET
        else:
            breakdown_period = RecurringTaskPeriod(_breakdown_period)

        _user_score_overview = d.pop("user_score_overview", UNSET)
        user_score_overview: Union[Unset, UserScoreOverview]
        if isinstance(_user_score_overview, Unset):
            user_score_overview = UNSET
        else:
            user_score_overview = UserScoreOverview.from_dict(_user_score_overview)

        report_period_result = cls(
            today=today,
            period=period,
            sources=sources,
            breakdowns=breakdowns,
            global_inbox_tasks_summary=global_inbox_tasks_summary,
            global_big_plans_summary=global_big_plans_summary,
            per_project_breakdown=per_project_breakdown,
            per_period_breakdown=per_period_breakdown,
            per_habit_breakdown=per_habit_breakdown,
            per_chore_breakdown=per_chore_breakdown,
            per_big_plan_breakdown=per_big_plan_breakdown,
            breakdown_period=breakdown_period,
            user_score_overview=user_score_overview,
        )

        report_period_result.additional_properties = d
        return report_period_result

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
