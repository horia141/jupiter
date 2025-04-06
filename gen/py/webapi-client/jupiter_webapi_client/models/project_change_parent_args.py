from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProjectChangeParentArgs")


@_attrs_define
class ProjectChangeParentArgs:
    """Project change parent args.

    Attributes:
        ref_id (str): A generic entity id.
        parent_project_ref_id (str): A generic entity id.
    """

    ref_id: str
    parent_project_ref_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        parent_project_ref_id = self.parent_project_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "parent_project_ref_id": parent_project_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        parent_project_ref_id = d.pop("parent_project_ref_id")

        project_change_parent_args = cls(
            ref_id=ref_id,
            parent_project_ref_id=parent_project_ref_id,
        )

        project_change_parent_args.additional_properties = d
        return project_change_parent_args

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
