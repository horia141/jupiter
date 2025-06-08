from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BigPlanSummary")


@_attrs_define
class BigPlanSummary:
    """Summary information about a big plan.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The big plan name.
        project_ref_id (str): A generic entity id.
        is_key (bool):
    """

    ref_id: str
    name: str
    project_ref_id: str
    is_key: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        project_ref_id = self.project_ref_id

        is_key = self.is_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "project_ref_id": project_ref_id,
                "is_key": is_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        project_ref_id = d.pop("project_ref_id")

        is_key = d.pop("is_key")

        big_plan_summary = cls(
            ref_id=ref_id,
            name=name,
            project_ref_id=project_ref_id,
            is_key=is_key,
        )

        big_plan_summary.additional_properties = d
        return big_plan_summary

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
