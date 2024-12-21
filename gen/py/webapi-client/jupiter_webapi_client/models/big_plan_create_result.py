from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="BigPlanCreateResult")


@_attrs_define
class BigPlanCreateResult:
    """Big plan create result.

    Attributes:
        new_big_plan (BigPlan): A big plan.
        new_time_plan_activity (Union['TimePlanActivity', None, Unset]):
    """

    new_big_plan: "BigPlan"
    new_time_plan_activity: Union["TimePlanActivity", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.time_plan_activity import TimePlanActivity

        new_big_plan = self.new_big_plan.to_dict()

        new_time_plan_activity: Union[Dict[str, Any], None, Unset]
        if isinstance(self.new_time_plan_activity, Unset):
            new_time_plan_activity = UNSET
        elif isinstance(self.new_time_plan_activity, TimePlanActivity):
            new_time_plan_activity = self.new_time_plan_activity.to_dict()
        else:
            new_time_plan_activity = self.new_time_plan_activity

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_big_plan": new_big_plan,
            }
        )
        if new_time_plan_activity is not UNSET:
            field_dict["new_time_plan_activity"] = new_time_plan_activity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.time_plan_activity import TimePlanActivity

        d = src_dict.copy()
        new_big_plan = BigPlan.from_dict(d.pop("new_big_plan"))

        def _parse_new_time_plan_activity(data: object) -> Union["TimePlanActivity", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                new_time_plan_activity_type_0 = TimePlanActivity.from_dict(data)

                return new_time_plan_activity_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TimePlanActivity", None, Unset], data)

        new_time_plan_activity = _parse_new_time_plan_activity(d.pop("new_time_plan_activity", UNSET))

        big_plan_create_result = cls(
            new_big_plan=new_big_plan,
            new_time_plan_activity=new_time_plan_activity,
        )

        big_plan_create_result.additional_properties = d
        return big_plan_create_result

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
