from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProjectCreateArgs")


@_attrs_define
class ProjectCreateArgs:
    """Project create args.

    Attributes:
        parent_project_ref_id (str): A generic entity id.
        name (str): The project name.
    """

    parent_project_ref_id: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        parent_project_ref_id = self.parent_project_ref_id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "parent_project_ref_id": parent_project_ref_id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        parent_project_ref_id = d.pop("parent_project_ref_id")

        name = d.pop("name")

        project_create_args = cls(
            parent_project_ref_id=parent_project_ref_id,
            name=name,
        )

        project_create_args.additional_properties = d
        return project_create_args

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
