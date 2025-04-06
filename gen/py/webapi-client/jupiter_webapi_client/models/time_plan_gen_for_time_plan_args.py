from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimePlanGenForTimePlanArgs")


@_attrs_define
class TimePlanGenForTimePlanArgs:
    """PersonFindArgs.

    Attributes:
        today (str): A date or possibly a datetime for the application.
        period (Union[None, Unset, list[RecurringTaskPeriod]]):
    """

    today: str
    period: Union[None, Unset, list[RecurringTaskPeriod]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        today = self.today

        period: Union[None, Unset, list[str]]
        if isinstance(self.period, Unset):
            period = UNSET
        elif isinstance(self.period, list):
            period = []
            for period_type_0_item_data in self.period:
                period_type_0_item = period_type_0_item_data.value
                period.append(period_type_0_item)

        else:
            period = self.period

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "today": today,
            }
        )
        if period is not UNSET:
            field_dict["period"] = period

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        today = d.pop("today")

        def _parse_period(data: object) -> Union[None, Unset, list[RecurringTaskPeriod]]:
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
            return cast(Union[None, Unset, list[RecurringTaskPeriod]], data)

        period = _parse_period(d.pop("period", UNSET))

        time_plan_gen_for_time_plan_args = cls(
            today=today,
            period=period,
        )

        time_plan_gen_for_time_plan_args.additional_properties = d
        return time_plan_gen_for_time_plan_args

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
