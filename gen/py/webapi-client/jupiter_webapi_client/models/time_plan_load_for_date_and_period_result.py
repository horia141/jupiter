from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.time_plan import TimePlan


T = TypeVar("T", bound="TimePlanLoadForDateAndPeriodResult")


@_attrs_define
class TimePlanLoadForDateAndPeriodResult:
    """Result.

    Attributes:
        sub_period_time_plans (list['TimePlan']):
        time_plan (Union['TimePlan', None, Unset]):
    """

    sub_period_time_plans: list["TimePlan"]
    time_plan: Union["TimePlan", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.time_plan import TimePlan

        sub_period_time_plans = []
        for sub_period_time_plans_item_data in self.sub_period_time_plans:
            sub_period_time_plans_item = sub_period_time_plans_item_data.to_dict()
            sub_period_time_plans.append(sub_period_time_plans_item)

        time_plan: Union[None, Unset, dict[str, Any]]
        if isinstance(self.time_plan, Unset):
            time_plan = UNSET
        elif isinstance(self.time_plan, TimePlan):
            time_plan = self.time_plan.to_dict()
        else:
            time_plan = self.time_plan

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sub_period_time_plans": sub_period_time_plans,
            }
        )
        if time_plan is not UNSET:
            field_dict["time_plan"] = time_plan

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_plan import TimePlan

        d = dict(src_dict)
        sub_period_time_plans = []
        _sub_period_time_plans = d.pop("sub_period_time_plans")
        for sub_period_time_plans_item_data in _sub_period_time_plans:
            sub_period_time_plans_item = TimePlan.from_dict(sub_period_time_plans_item_data)

            sub_period_time_plans.append(sub_period_time_plans_item)

        def _parse_time_plan(data: object) -> Union["TimePlan", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                time_plan_type_0 = TimePlan.from_dict(data)

                return time_plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TimePlan", None, Unset], data)

        time_plan = _parse_time_plan(d.pop("time_plan", UNSET))

        time_plan_load_for_date_and_period_result = cls(
            sub_period_time_plans=sub_period_time_plans,
            time_plan=time_plan,
        )

        time_plan_load_for_date_and_period_result.additional_properties = d
        return time_plan_load_for_date_and_period_result

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
