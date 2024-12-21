from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_plan_activity_target import TimePlanActivityTarget

T = TypeVar("T", bound="TimePlanActivityFindForTargetArgs")


@_attrs_define
class TimePlanActivityFindForTargetArgs:
    """Args.

    Attributes:
        allow_archived (bool):
        target (TimePlanActivityTarget): The target of an activity.
        target_ref_id (str): A generic entity id.
    """

    allow_archived: bool
    target: TimePlanActivityTarget
    target_ref_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        allow_archived = self.allow_archived

        target = self.target.value

        target_ref_id = self.target_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allow_archived": allow_archived,
                "target": target,
                "target_ref_id": target_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        allow_archived = d.pop("allow_archived")

        target = TimePlanActivityTarget(d.pop("target"))

        target_ref_id = d.pop("target_ref_id")

        time_plan_activity_find_for_target_args = cls(
            allow_archived=allow_archived,
            target=target,
            target_ref_id=target_ref_id,
        )

        time_plan_activity_find_for_target_args.additional_properties = d
        return time_plan_activity_find_for_target_args

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
