from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.note import Note
    from ..models.time_plan import TimePlan
    from ..models.time_plan_activity import TimePlanActivity


T = TypeVar("T", bound="TimePlanLoadResult")


@_attrs_define
class TimePlanLoadResult:
    """Result.

    Attributes:
        time_plan (TimePlan): A plan for a particular period of time.
        note (Note): A note in the notebook.
        activities (List['TimePlanActivity']):
        sub_period_time_plans (List['TimePlan']):
    """

    time_plan: "TimePlan"
    note: "Note"
    activities: List["TimePlanActivity"]
    sub_period_time_plans: List["TimePlan"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        time_plan = self.time_plan.to_dict()

        note = self.note.to_dict()

        activities = []
        for activities_item_data in self.activities:
            activities_item = activities_item_data.to_dict()
            activities.append(activities_item)

        sub_period_time_plans = []
        for sub_period_time_plans_item_data in self.sub_period_time_plans:
            sub_period_time_plans_item = sub_period_time_plans_item_data.to_dict()
            sub_period_time_plans.append(sub_period_time_plans_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan": time_plan,
                "note": note,
                "activities": activities,
                "sub_period_time_plans": sub_period_time_plans,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.note import Note
        from ..models.time_plan import TimePlan
        from ..models.time_plan_activity import TimePlanActivity

        d = src_dict.copy()
        time_plan = TimePlan.from_dict(d.pop("time_plan"))

        note = Note.from_dict(d.pop("note"))

        activities = []
        _activities = d.pop("activities")
        for activities_item_data in _activities:
            activities_item = TimePlanActivity.from_dict(activities_item_data)

            activities.append(activities_item)

        sub_period_time_plans = []
        _sub_period_time_plans = d.pop("sub_period_time_plans")
        for sub_period_time_plans_item_data in _sub_period_time_plans:
            sub_period_time_plans_item = TimePlan.from_dict(sub_period_time_plans_item_data)

            sub_period_time_plans.append(sub_period_time_plans_item)

        time_plan_load_result = cls(
            time_plan=time_plan,
            note=note,
            activities=activities,
            sub_period_time_plans=sub_period_time_plans,
        )

        time_plan_load_result.additional_properties = d
        return time_plan_load_result

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
