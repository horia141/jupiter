from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_feasability import TimePlanActivityFeasability
from ..models.time_plan_activity_kind import TimePlanActivityKind

T = TypeVar("T", bound="TimePlanActivityCreateForInboxTaskArgs")


@_attrs_define
class TimePlanActivityCreateForInboxTaskArgs:
    """Args.

    Attributes:
        time_plan_ref_id (str): A generic entity id.
        inbox_task_ref_id (str): A generic entity id.
        kind (TimePlanActivityKind): The kind of a time plan activity.
        feasability (TimePlanActivityFeasability): The feasability of a particular activity within a plan.
    """

    time_plan_ref_id: str
    inbox_task_ref_id: str
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        time_plan_ref_id = self.time_plan_ref_id

        inbox_task_ref_id = self.inbox_task_ref_id

        kind = self.kind.value

        feasability = self.feasability.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan_ref_id": time_plan_ref_id,
                "inbox_task_ref_id": inbox_task_ref_id,
                "kind": kind,
                "feasability": feasability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        time_plan_ref_id = d.pop("time_plan_ref_id")

        inbox_task_ref_id = d.pop("inbox_task_ref_id")

        kind = TimePlanActivityKind(d.pop("kind"))

        feasability = TimePlanActivityFeasability(d.pop("feasability"))

        time_plan_activity_create_for_inbox_task_args = cls(
            time_plan_ref_id=time_plan_ref_id,
            inbox_task_ref_id=inbox_task_ref_id,
            kind=kind,
            feasability=feasability,
        )

        time_plan_activity_create_for_inbox_task_args.additional_properties = d
        return time_plan_activity_create_for_inbox_task_args

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
