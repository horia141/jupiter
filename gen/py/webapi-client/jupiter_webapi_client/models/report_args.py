from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

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
        today (Union[None, Unset, str]):
        sources (Union[None, Unset, list[InboxTaskSource]]):
        breakdowns (Union[None, Unset, list[ReportBreakdown]]):
        filter_project_ref_ids (Union[None, Unset, list[str]]):
        filter_big_plan_ref_ids (Union[None, Unset, list[str]]):
        filter_habit_ref_ids (Union[None, Unset, list[str]]):
        filter_chore_ref_ids (Union[None, Unset, list[str]]):
        filter_metric_ref_ids (Union[None, Unset, list[str]]):
        filter_person_ref_ids (Union[None, Unset, list[str]]):
        filter_slack_task_ref_ids (Union[None, Unset, list[str]]):
        filter_email_task_ref_ids (Union[None, Unset, list[str]]):
        breakdown_period (Union[None, RecurringTaskPeriod, Unset]):
    """

    period: RecurringTaskPeriod
    today: Union[None, Unset, str] = UNSET
    sources: Union[None, Unset, list[InboxTaskSource]] = UNSET
    breakdowns: Union[None, Unset, list[ReportBreakdown]] = UNSET
    filter_project_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_big_plan_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_habit_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_chore_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_metric_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_person_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_slack_task_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_email_task_ref_ids: Union[None, Unset, list[str]] = UNSET
    breakdown_period: Union[None, RecurringTaskPeriod, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period.value

        today: Union[None, Unset, str]
        if isinstance(self.today, Unset):
            today = UNSET
        else:
            today = self.today

        sources: Union[None, Unset, list[str]]
        if isinstance(self.sources, Unset):
            sources = UNSET
        elif isinstance(self.sources, list):
            sources = []
            for sources_type_0_item_data in self.sources:
                sources_type_0_item = sources_type_0_item_data.value
                sources.append(sources_type_0_item)

        else:
            sources = self.sources

        breakdowns: Union[None, Unset, list[str]]
        if isinstance(self.breakdowns, Unset):
            breakdowns = UNSET
        elif isinstance(self.breakdowns, list):
            breakdowns = []
            for breakdowns_type_0_item_data in self.breakdowns:
                breakdowns_type_0_item = breakdowns_type_0_item_data.value
                breakdowns.append(breakdowns_type_0_item)

        else:
            breakdowns = self.breakdowns

        filter_project_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = UNSET
        elif isinstance(self.filter_project_ref_ids, list):
            filter_project_ref_ids = self.filter_project_ref_ids

        else:
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_big_plan_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_big_plan_ref_ids, Unset):
            filter_big_plan_ref_ids = UNSET
        elif isinstance(self.filter_big_plan_ref_ids, list):
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        else:
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        filter_habit_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = UNSET
        elif isinstance(self.filter_habit_ref_ids, list):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        else:
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_chore_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_chore_ref_ids, Unset):
            filter_chore_ref_ids = UNSET
        elif isinstance(self.filter_chore_ref_ids, list):
            filter_chore_ref_ids = self.filter_chore_ref_ids

        else:
            filter_chore_ref_ids = self.filter_chore_ref_ids

        filter_metric_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_metric_ref_ids, Unset):
            filter_metric_ref_ids = UNSET
        elif isinstance(self.filter_metric_ref_ids, list):
            filter_metric_ref_ids = self.filter_metric_ref_ids

        else:
            filter_metric_ref_ids = self.filter_metric_ref_ids

        filter_person_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = UNSET
        elif isinstance(self.filter_person_ref_ids, list):
            filter_person_ref_ids = self.filter_person_ref_ids

        else:
            filter_person_ref_ids = self.filter_person_ref_ids

        filter_slack_task_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_slack_task_ref_ids, Unset):
            filter_slack_task_ref_ids = UNSET
        elif isinstance(self.filter_slack_task_ref_ids, list):
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        else:
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        filter_email_task_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_email_task_ref_ids, Unset):
            filter_email_task_ref_ids = UNSET
        elif isinstance(self.filter_email_task_ref_ids, list):
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        else:
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        breakdown_period: Union[None, Unset, str]
        if isinstance(self.breakdown_period, Unset):
            breakdown_period = UNSET
        elif isinstance(self.breakdown_period, RecurringTaskPeriod):
            breakdown_period = self.breakdown_period.value
        else:
            breakdown_period = self.breakdown_period

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        period = RecurringTaskPeriod(d.pop("period"))

        def _parse_today(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        today = _parse_today(d.pop("today", UNSET))

        def _parse_sources(data: object) -> Union[None, Unset, list[InboxTaskSource]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sources_type_0 = []
                _sources_type_0 = data
                for sources_type_0_item_data in _sources_type_0:
                    sources_type_0_item = InboxTaskSource(sources_type_0_item_data)

                    sources_type_0.append(sources_type_0_item)

                return sources_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[InboxTaskSource]], data)

        sources = _parse_sources(d.pop("sources", UNSET))

        def _parse_breakdowns(data: object) -> Union[None, Unset, list[ReportBreakdown]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                breakdowns_type_0 = []
                _breakdowns_type_0 = data
                for breakdowns_type_0_item_data in _breakdowns_type_0:
                    breakdowns_type_0_item = ReportBreakdown(breakdowns_type_0_item_data)

                    breakdowns_type_0.append(breakdowns_type_0_item)

                return breakdowns_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[ReportBreakdown]], data)

        breakdowns = _parse_breakdowns(d.pop("breakdowns", UNSET))

        def _parse_filter_project_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_project_ref_ids_type_0 = cast(list[str], data)

                return filter_project_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_project_ref_ids = _parse_filter_project_ref_ids(d.pop("filter_project_ref_ids", UNSET))

        def _parse_filter_big_plan_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_big_plan_ref_ids_type_0 = cast(list[str], data)

                return filter_big_plan_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_big_plan_ref_ids = _parse_filter_big_plan_ref_ids(d.pop("filter_big_plan_ref_ids", UNSET))

        def _parse_filter_habit_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_habit_ref_ids_type_0 = cast(list[str], data)

                return filter_habit_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_habit_ref_ids = _parse_filter_habit_ref_ids(d.pop("filter_habit_ref_ids", UNSET))

        def _parse_filter_chore_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_chore_ref_ids_type_0 = cast(list[str], data)

                return filter_chore_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_chore_ref_ids = _parse_filter_chore_ref_ids(d.pop("filter_chore_ref_ids", UNSET))

        def _parse_filter_metric_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_metric_ref_ids_type_0 = cast(list[str], data)

                return filter_metric_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_metric_ref_ids = _parse_filter_metric_ref_ids(d.pop("filter_metric_ref_ids", UNSET))

        def _parse_filter_person_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_person_ref_ids_type_0 = cast(list[str], data)

                return filter_person_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_person_ref_ids = _parse_filter_person_ref_ids(d.pop("filter_person_ref_ids", UNSET))

        def _parse_filter_slack_task_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_slack_task_ref_ids_type_0 = cast(list[str], data)

                return filter_slack_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_slack_task_ref_ids = _parse_filter_slack_task_ref_ids(d.pop("filter_slack_task_ref_ids", UNSET))

        def _parse_filter_email_task_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_email_task_ref_ids_type_0 = cast(list[str], data)

                return filter_email_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_email_task_ref_ids = _parse_filter_email_task_ref_ids(d.pop("filter_email_task_ref_ids", UNSET))

        def _parse_breakdown_period(data: object) -> Union[None, RecurringTaskPeriod, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                breakdown_period_type_0 = RecurringTaskPeriod(data)

                return breakdown_period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RecurringTaskPeriod, Unset], data)

        breakdown_period = _parse_breakdown_period(d.pop("breakdown_period", UNSET))

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
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
