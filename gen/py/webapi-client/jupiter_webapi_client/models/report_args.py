from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inbox_task_source import InboxTaskSource
from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.report_breakdown import ReportBreakdown
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportArgs")


@_attrs_define
class ReportArgs:
    """Report args.

    Attributes:
        period (RecurringTaskPeriod): A period for a particular task.
        today (Union[Unset, str]): A date or possibly a datetime for the application.
        sources (Union[Unset, List[InboxTaskSource]]):
        breakdowns (Union[Unset, List[ReportBreakdown]]):
        filter_project_ref_ids (Union[Unset, List[str]]):
        filter_big_plan_ref_ids (Union[Unset, List[str]]):
        filter_habit_ref_ids (Union[Unset, List[str]]):
        filter_chore_ref_ids (Union[Unset, List[str]]):
        filter_metric_ref_ids (Union[Unset, List[str]]):
        filter_person_ref_ids (Union[Unset, List[str]]):
        filter_slack_task_ref_ids (Union[Unset, List[str]]):
        filter_email_task_ref_ids (Union[Unset, List[str]]):
        breakdown_period (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
    """

    period: RecurringTaskPeriod
    today: Union[Unset, str] = UNSET
    sources: Union[Unset, List[InboxTaskSource]] = UNSET
    breakdowns: Union[Unset, List[ReportBreakdown]] = UNSET
    filter_project_ref_ids: Union[Unset, List[str]] = UNSET
    filter_big_plan_ref_ids: Union[Unset, List[str]] = UNSET
    filter_habit_ref_ids: Union[Unset, List[str]] = UNSET
    filter_chore_ref_ids: Union[Unset, List[str]] = UNSET
    filter_metric_ref_ids: Union[Unset, List[str]] = UNSET
    filter_person_ref_ids: Union[Unset, List[str]] = UNSET
    filter_slack_task_ref_ids: Union[Unset, List[str]] = UNSET
    filter_email_task_ref_ids: Union[Unset, List[str]] = UNSET
    breakdown_period: Union[Unset, RecurringTaskPeriod] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        period = self.period.value

        today = self.today

        sources: Union[Unset, List[str]] = UNSET
        if not isinstance(self.sources, Unset):
            sources = []
            for sources_item_data in self.sources:
                sources_item = sources_item_data.value
                sources.append(sources_item)

        breakdowns: Union[Unset, List[str]] = UNSET
        if not isinstance(self.breakdowns, Unset):
            breakdowns = []
            for breakdowns_item_data in self.breakdowns:
                breakdowns_item = breakdowns_item_data.value
                breakdowns.append(breakdowns_item)

        filter_project_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_big_plan_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_big_plan_ref_ids, Unset):
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        filter_habit_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_chore_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_chore_ref_ids, Unset):
            filter_chore_ref_ids = self.filter_chore_ref_ids

        filter_metric_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_metric_ref_ids, Unset):
            filter_metric_ref_ids = self.filter_metric_ref_ids

        filter_person_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = self.filter_person_ref_ids

        filter_slack_task_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_slack_task_ref_ids, Unset):
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        filter_email_task_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_email_task_ref_ids, Unset):
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        breakdown_period: Union[Unset, str] = UNSET
        if not isinstance(self.breakdown_period, Unset):
            breakdown_period = self.breakdown_period.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
            }
        )
        if today is not UNSET:
            field_dict["today"] = today
        if sources is not UNSET:
            field_dict["sources"] = sources
        if breakdowns is not UNSET:
            field_dict["breakdowns"] = breakdowns
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids
        if filter_big_plan_ref_ids is not UNSET:
            field_dict["filter_big_plan_ref_ids"] = filter_big_plan_ref_ids
        if filter_habit_ref_ids is not UNSET:
            field_dict["filter_habit_ref_ids"] = filter_habit_ref_ids
        if filter_chore_ref_ids is not UNSET:
            field_dict["filter_chore_ref_ids"] = filter_chore_ref_ids
        if filter_metric_ref_ids is not UNSET:
            field_dict["filter_metric_ref_ids"] = filter_metric_ref_ids
        if filter_person_ref_ids is not UNSET:
            field_dict["filter_person_ref_ids"] = filter_person_ref_ids
        if filter_slack_task_ref_ids is not UNSET:
            field_dict["filter_slack_task_ref_ids"] = filter_slack_task_ref_ids
        if filter_email_task_ref_ids is not UNSET:
            field_dict["filter_email_task_ref_ids"] = filter_email_task_ref_ids
        if breakdown_period is not UNSET:
            field_dict["breakdown_period"] = breakdown_period

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        period = RecurringTaskPeriod(d.pop("period"))

        today = d.pop("today", UNSET)

        sources = []
        _sources = d.pop("sources", UNSET)
        for sources_item_data in _sources or []:
            sources_item = InboxTaskSource(sources_item_data)

            sources.append(sources_item)

        breakdowns = []
        _breakdowns = d.pop("breakdowns", UNSET)
        for breakdowns_item_data in _breakdowns or []:
            breakdowns_item = ReportBreakdown(breakdowns_item_data)

            breakdowns.append(breakdowns_item)

        filter_project_ref_ids = cast(List[str], d.pop("filter_project_ref_ids", UNSET))

        filter_big_plan_ref_ids = cast(List[str], d.pop("filter_big_plan_ref_ids", UNSET))

        filter_habit_ref_ids = cast(List[str], d.pop("filter_habit_ref_ids", UNSET))

        filter_chore_ref_ids = cast(List[str], d.pop("filter_chore_ref_ids", UNSET))

        filter_metric_ref_ids = cast(List[str], d.pop("filter_metric_ref_ids", UNSET))

        filter_person_ref_ids = cast(List[str], d.pop("filter_person_ref_ids", UNSET))

        filter_slack_task_ref_ids = cast(List[str], d.pop("filter_slack_task_ref_ids", UNSET))

        filter_email_task_ref_ids = cast(List[str], d.pop("filter_email_task_ref_ids", UNSET))

        _breakdown_period = d.pop("breakdown_period", UNSET)
        breakdown_period: Union[Unset, RecurringTaskPeriod]
        if isinstance(_breakdown_period, Unset):
            breakdown_period = UNSET
        else:
            breakdown_period = RecurringTaskPeriod(_breakdown_period)

        report_args = cls(
            period=period,
            today=today,
            sources=sources,
            breakdowns=breakdowns,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_big_plan_ref_ids=filter_big_plan_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
            filter_chore_ref_ids=filter_chore_ref_ids,
            filter_metric_ref_ids=filter_metric_ref_ids,
            filter_person_ref_ids=filter_person_ref_ids,
            filter_slack_task_ref_ids=filter_slack_task_ref_ids,
            filter_email_task_ref_ids=filter_email_task_ref_ids,
            breakdown_period=breakdown_period,
        )

        report_args.additional_properties = d
        return report_args

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
