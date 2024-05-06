from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanActivityCreateForBigPlanResult")


@_attrs_define
class TimePlanActivityCreateForBigPlanResult:
    """Result.

    Attributes:
        new_time_plan_activity (TimePlanActivity): A certain activity that happens in a plan.
    """

    new_time_plan_activity: "TimePlanActivity"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_time_plan_activity = self.new_time_plan_activity.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_time_plan_activity": new_time_plan_activity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_plan_activity import TimePlanActivity

        d = src_dict.copy()
        new_time_plan_activity = TimePlanActivity.from_dict(d.pop("new_time_plan_activity"))

        time_plan_activity_create_for_big_plan_result = cls(
            new_time_plan_activity=new_time_plan_activity,
        )

        time_plan_activity_create_for_big_plan_result.additional_properties = d
        return time_plan_activity_create_for_big_plan_result

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
