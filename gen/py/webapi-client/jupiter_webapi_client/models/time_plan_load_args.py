from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TimePlanLoadArgs")


@_attrs_define
class TimePlanLoadArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        include_targets (bool):
        include_completed_nontarget (bool):
        include_other_time_plans (bool):
    """

    ref_id: str
    allow_archived: bool
    include_targets: bool
    include_completed_nontarget: bool
    include_other_time_plans: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        include_targets = self.include_targets

        include_completed_nontarget = self.include_completed_nontarget

        include_other_time_plans = self.include_other_time_plans

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
                "include_targets": include_targets,
                "include_completed_nontarget": include_completed_nontarget,
                "include_other_time_plans": include_other_time_plans,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        include_targets = d.pop("include_targets")

        include_completed_nontarget = d.pop("include_completed_nontarget")

        include_other_time_plans = d.pop("include_other_time_plans")

        time_plan_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            include_targets=include_targets,
            include_completed_nontarget=include_completed_nontarget,
            include_other_time_plans=include_other_time_plans,
        )

        time_plan_load_args.additional_properties = d
        return time_plan_load_args

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
