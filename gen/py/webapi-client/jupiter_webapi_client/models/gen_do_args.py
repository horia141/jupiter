from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="GenDoArgs")


@_attrs_define
class GenDoArgs:
    """PersonFindArgs.

    Attributes:
        gen_even_if_not_modified (bool):
        today (Union[None, Unset, str]):
        gen_targets (Union[List[SyncTarget], None, Unset]):
        period (Union[List[RecurringTaskPeriod], None, Unset]):
        filter_project_ref_ids (Union[List[str], None, Unset]):
        filter_habit_ref_ids (Union[List[str], None, Unset]):
        filter_chore_ref_ids (Union[List[str], None, Unset]):
        filter_metric_ref_ids (Union[List[str], None, Unset]):
        filter_person_ref_ids (Union[List[str], None, Unset]):
        filter_slack_task_ref_ids (Union[List[str], None, Unset]):
        filter_email_task_ref_ids (Union[List[str], None, Unset]):
    """

    gen_even_if_not_modified: bool
    today: Union[None, Unset, str] = UNSET
    gen_targets: Union[List[SyncTarget], None, Unset] = UNSET
    period: Union[List[RecurringTaskPeriod], None, Unset] = UNSET
    filter_project_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_habit_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_chore_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_metric_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_person_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_slack_task_ref_ids: Union[List[str], None, Unset] = UNSET
    filter_email_task_ref_ids: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        gen_even_if_not_modified = self.gen_even_if_not_modified

        today: Union[None, Unset, str]
        if isinstance(self.today, Unset):
            today = UNSET
        else:
            today = self.today

        gen_targets: Union[List[str], None, Unset]
        if isinstance(self.gen_targets, Unset):
            gen_targets = UNSET
        elif isinstance(self.gen_targets, list):
            gen_targets = []
            for gen_targets_type_0_item_data in self.gen_targets:
                gen_targets_type_0_item = gen_targets_type_0_item_data.value
                gen_targets.append(gen_targets_type_0_item)

        else:
            gen_targets = self.gen_targets

        period: Union[List[str], None, Unset]
        if isinstance(self.period, Unset):
            period = UNSET
        elif isinstance(self.period, list):
            period = []
            for period_type_0_item_data in self.period:
                period_type_0_item = period_type_0_item_data.value
                period.append(period_type_0_item)

        else:
            period = self.period

        filter_project_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_project_ref_ids, Unset):
            filter_project_ref_ids = UNSET
        elif isinstance(self.filter_project_ref_ids, list):
            filter_project_ref_ids = self.filter_project_ref_ids

        else:
            filter_project_ref_ids = self.filter_project_ref_ids

        filter_habit_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = UNSET
        elif isinstance(self.filter_habit_ref_ids, list):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        else:
            filter_habit_ref_ids = self.filter_habit_ref_ids

        filter_chore_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_chore_ref_ids, Unset):
            filter_chore_ref_ids = UNSET
        elif isinstance(self.filter_chore_ref_ids, list):
            filter_chore_ref_ids = self.filter_chore_ref_ids

        else:
            filter_chore_ref_ids = self.filter_chore_ref_ids

        filter_metric_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_metric_ref_ids, Unset):
            filter_metric_ref_ids = UNSET
        elif isinstance(self.filter_metric_ref_ids, list):
            filter_metric_ref_ids = self.filter_metric_ref_ids

        else:
            filter_metric_ref_ids = self.filter_metric_ref_ids

        filter_person_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_person_ref_ids, Unset):
            filter_person_ref_ids = UNSET
        elif isinstance(self.filter_person_ref_ids, list):
            filter_person_ref_ids = self.filter_person_ref_ids

        else:
            filter_person_ref_ids = self.filter_person_ref_ids

        filter_slack_task_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_slack_task_ref_ids, Unset):
            filter_slack_task_ref_ids = UNSET
        elif isinstance(self.filter_slack_task_ref_ids, list):
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        else:
            filter_slack_task_ref_ids = self.filter_slack_task_ref_ids

        filter_email_task_ref_ids: Union[List[str], None, Unset]
        if isinstance(self.filter_email_task_ref_ids, Unset):
            filter_email_task_ref_ids = UNSET
        elif isinstance(self.filter_email_task_ref_ids, list):
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        else:
            filter_email_task_ref_ids = self.filter_email_task_ref_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
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
        gen_even_if_not_modified = d.pop("gen_even_if_not_modified")

        def _parse_today(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        today = _parse_today(d.pop("today", UNSET))

        def _parse_gen_targets(data: object) -> Union[List[SyncTarget], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                gen_targets_type_0 = []
                _gen_targets_type_0 = data
                for gen_targets_type_0_item_data in _gen_targets_type_0:
                    gen_targets_type_0_item = SyncTarget(gen_targets_type_0_item_data)

                    gen_targets_type_0.append(gen_targets_type_0_item)

                return gen_targets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[SyncTarget], None, Unset], data)

        gen_targets = _parse_gen_targets(d.pop("gen_targets", UNSET))

        def _parse_period(data: object) -> Union[List[RecurringTaskPeriod], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                period_type_0 = []
                _period_type_0 = data
                for period_type_0_item_data in _period_type_0:
                    period_type_0_item = RecurringTaskPeriod(period_type_0_item_data)

                    period_type_0.append(period_type_0_item)

                return period_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[RecurringTaskPeriod], None, Unset], data)

        period = _parse_period(d.pop("period", UNSET))

        def _parse_filter_project_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_project_ref_ids_type_0 = cast(List[str], data)

                return filter_project_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_project_ref_ids = _parse_filter_project_ref_ids(d.pop("filter_project_ref_ids", UNSET))

        def _parse_filter_habit_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_habit_ref_ids_type_0 = cast(List[str], data)

                return filter_habit_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_habit_ref_ids = _parse_filter_habit_ref_ids(d.pop("filter_habit_ref_ids", UNSET))

        def _parse_filter_chore_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_chore_ref_ids_type_0 = cast(List[str], data)

                return filter_chore_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_chore_ref_ids = _parse_filter_chore_ref_ids(d.pop("filter_chore_ref_ids", UNSET))

        def _parse_filter_metric_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_metric_ref_ids_type_0 = cast(List[str], data)

                return filter_metric_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_metric_ref_ids = _parse_filter_metric_ref_ids(d.pop("filter_metric_ref_ids", UNSET))

        def _parse_filter_person_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_person_ref_ids_type_0 = cast(List[str], data)

                return filter_person_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_person_ref_ids = _parse_filter_person_ref_ids(d.pop("filter_person_ref_ids", UNSET))

        def _parse_filter_slack_task_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_slack_task_ref_ids_type_0 = cast(List[str], data)

                return filter_slack_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_slack_task_ref_ids = _parse_filter_slack_task_ref_ids(d.pop("filter_slack_task_ref_ids", UNSET))

        def _parse_filter_email_task_ref_ids(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_email_task_ref_ids_type_0 = cast(List[str], data)

                return filter_email_task_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_email_task_ref_ids = _parse_filter_email_task_ref_ids(d.pop("filter_email_task_ref_ids", UNSET))

        gen_do_args = cls(
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
