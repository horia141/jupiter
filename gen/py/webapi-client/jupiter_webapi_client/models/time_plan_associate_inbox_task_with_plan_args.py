from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_feasability import TimePlanActivityFeasability
from ..models.time_plan_activity_kind import TimePlanActivityKind

T = TypeVar("T", bound="TimePlanAssociateInboxTaskWithPlanArgs")


@_attrs_define
class TimePlanAssociateInboxTaskWithPlanArgs:
    """Args.

    Attributes:
        inbox_task_ref_id (str): A generic entity id.
        time_plan_ref_ids (list[str]):
        kind (TimePlanActivityKind): The kind of a time plan activity.
        feasability (TimePlanActivityFeasability): The feasability of a particular activity within a plan.
    """

    inbox_task_ref_id: str
    time_plan_ref_ids: list[str]
    kind: TimePlanActivityKind
    feasability: TimePlanActivityFeasability
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inbox_task_ref_id = self.inbox_task_ref_id

        time_plan_ref_ids = self.time_plan_ref_ids

        kind = self.kind.value

        feasability = self.feasability.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbox_task_ref_id": inbox_task_ref_id,
                "time_plan_ref_ids": time_plan_ref_ids,
                "kind": kind,
                "feasability": feasability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        inbox_task_ref_id = d.pop("inbox_task_ref_id")

        time_plan_ref_ids = cast(list[str], d.pop("time_plan_ref_ids"))

        kind = TimePlanActivityKind(d.pop("kind"))

        feasability = TimePlanActivityFeasability(d.pop("feasability"))

        time_plan_associate_inbox_task_with_plan_args = cls(
            inbox_task_ref_id=inbox_task_ref_id,
            time_plan_ref_ids=time_plan_ref_ids,
            kind=kind,
            feasability=feasability,
        )

        time_plan_associate_inbox_task_with_plan_args.additional_properties = d
        return time_plan_associate_inbox_task_with_plan_args

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
