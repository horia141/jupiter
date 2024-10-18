from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanActivityFindForTargetResult")


@_attrs_define
class TimePlanActivityFindForTargetResult:
    """Result.

    Attributes:
        activities (List['TimePlanActivity']):
    """

    activities: List["TimePlanActivity"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        activities = []
        for activities_item_data in self.activities:
            activities_item = activities_item_data.to_dict()
            activities.append(activities_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "activities": activities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_plan_activity import TimePlanActivity

        d = src_dict.copy()
        activities = []
        _activities = d.pop("activities")
        for activities_item_data in _activities:
            activities_item = TimePlanActivity.from_dict(activities_item_data)

            activities.append(activities_item)

        time_plan_activity_find_for_target_result = cls(
            activities=activities,
        )

        time_plan_activity_find_for_target_result.additional_properties = d
        return time_plan_activity_find_for_target_result

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
