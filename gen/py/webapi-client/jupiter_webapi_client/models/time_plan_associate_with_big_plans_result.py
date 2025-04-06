from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanAssociateWithBigPlansResult")


@_attrs_define
class TimePlanAssociateWithBigPlansResult:
    """Result.

    Attributes:
        new_time_plan_activities (list['TimePlanActivity']):
    """

    new_time_plan_activities: list["TimePlanActivity"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_time_plan_activities = []
        for new_time_plan_activities_item_data in self.new_time_plan_activities:
            new_time_plan_activities_item = new_time_plan_activities_item_data.to_dict()
            new_time_plan_activities.append(new_time_plan_activities_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_time_plan_activities": new_time_plan_activities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_plan_activity import TimePlanActivity

        d = dict(src_dict)
        new_time_plan_activities = []
        _new_time_plan_activities = d.pop("new_time_plan_activities")
        for new_time_plan_activities_item_data in _new_time_plan_activities:
            new_time_plan_activities_item = TimePlanActivity.from_dict(new_time_plan_activities_item_data)

            new_time_plan_activities.append(new_time_plan_activities_item)

        time_plan_associate_with_big_plans_result = cls(
            new_time_plan_activities=new_time_plan_activities,
        )

        time_plan_associate_with_big_plans_result.additional_properties = d
        return time_plan_associate_with_big_plans_result

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
