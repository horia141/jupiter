from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="GenDoArgs")


@_attrs_define
class GenDoArgs:
    """PersonFindArgs.

    Attributes:
        source (EventSource): The source of the modification which this event records.
        gen_even_if_not_modified (bool):
        today (Union[Unset, str]): A date or possibly a datetime for the application.
        gen_targets (Union[Unset, List[SyncTarget]]):
        period (Union[Unset, List[RecurringTaskPeriod]]):
        filter_project_ref_ids (Union[Unset, List[str]]):
        filter_habit_ref_ids (Union[Unset, List[str]]):
        filter_chore_ref_ids (Union[Unset, List[str]]):
        filter_metric_ref_ids (Union[Unset, List[str]]):
        filter_person_ref_ids (Union[Unset, List[str]]):
        filter_slack_task_ref_ids (Union[Unset, List[str]]):
        filter_email_task_ref_ids (Union[Unset, List[str]]):
    """

    source: EventSource
    gen_even_if_not_modified: bool
    today: Union[Unset, str] = UNSET
    gen_targets: Union[Unset, List[SyncTarget]] = UNSET
    period: Union[Unset, List[RecurringTaskPeriod]] = UNSET
    filter_project_ref_ids: Union[Unset, List[str]] = UNSET
    filter_habit_ref_ids: Union[Unset, List[str]] = UNSET
    filter_chore_ref_ids: Union[Unset, List[str]] = UNSET
    filter_metric_ref_ids: Union[Unset, List[str]] = UNSET
    filter_person_ref_ids: Union[Unset, List[str]] = UNSET
    filter_slack_task_ref_ids: Union[Unset, List[str]] = UNSET
    filter_email_task_ref_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source = self.source.value

        gen_even_if_not_modified = self.gen_even_if_not_modified

        today = self.today

        gen_targets: Union[Unset, List[str]] = UNSET
        if not isinstance(self.gen_targets, Unset):
            gen_targets = []
            for gen_targets_item_data in self.gen_targets:
                gen_targets_item = gen_targets_item_data.value
                gen_targets.append(gen_targets_item)

        period: Union[Unset, List[str]] = UNSET
        if not isinstance(self.period, Unset):
            period = []
            for period_item_data in self.period:
                period_item = period_item_data.value
                period.append(period_item)

        filter_project_ref_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = self.filter_project_ref_ids

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

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "gen_even_if_not_modified": gen_even_if_not_modified,
            }
        )
        if today is not UNSET:
            field_dict["today"] = today
        if gen_targets is not UNSET:
            field_dict["gen_targets"] = gen_targets
        if period is not UNSET:
            field_dict["period"] = period
        if filter_project_ref_ids is not UNSET:
            field_dict["filter_project_ref_ids"] = filter_project_ref_ids
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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source = EventSource(d.pop("source"))

        gen_even_if_not_modified = d.pop("gen_even_if_not_modified")

        today = d.pop("today", UNSET)

        gen_targets = []
        _gen_targets = d.pop("gen_targets", UNSET)
        for gen_targets_item_data in _gen_targets or []:
            gen_targets_item = SyncTarget(gen_targets_item_data)

            gen_targets.append(gen_targets_item)

        period = []
        _period = d.pop("period", UNSET)
        for period_item_data in _period or []:
            period_item = RecurringTaskPeriod(period_item_data)

            period.append(period_item)

        filter_project_ref_ids = cast(List[str], d.pop("filter_project_ref_ids", UNSET))

        filter_habit_ref_ids = cast(List[str], d.pop("filter_habit_ref_ids", UNSET))

        filter_chore_ref_ids = cast(List[str], d.pop("filter_chore_ref_ids", UNSET))

        filter_metric_ref_ids = cast(List[str], d.pop("filter_metric_ref_ids", UNSET))

        filter_person_ref_ids = cast(List[str], d.pop("filter_person_ref_ids", UNSET))

        filter_slack_task_ref_ids = cast(List[str], d.pop("filter_slack_task_ref_ids", UNSET))

        filter_email_task_ref_ids = cast(List[str], d.pop("filter_email_task_ref_ids", UNSET))

        gen_do_args = cls(
            source=source,
            gen_even_if_not_modified=gen_even_if_not_modified,
            today=today,
            gen_targets=gen_targets,
            period=period,
            filter_project_ref_ids=filter_project_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
            filter_chore_ref_ids=filter_chore_ref_ids,
            filter_metric_ref_ids=filter_metric_ref_ids,
            filter_person_ref_ids=filter_person_ref_ids,
            filter_slack_task_ref_ids=filter_slack_task_ref_ids,
            filter_email_task_ref_ids=filter_email_task_ref_ids,
        )

        gen_do_args.additional_properties = d
        return gen_do_args

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
