from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectSummary")


@_attrs_define
class ProjectSummary:
    """Summary information about a project.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The project name.
        order_of_child_projects (list[str]):
        parent_project_ref_id (Union[None, Unset, str]):
    """

    ref_id: str
    name: str
    order_of_child_projects: list[str]
    parent_project_ref_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        order_of_child_projects = self.order_of_child_projects

        parent_project_ref_id: Union[None, Unset, str]
        if isinstance(self.parent_project_ref_id, Unset):
            parent_project_ref_id = UNSET
        else:
            parent_project_ref_id = self.parent_project_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "order_of_child_projects": order_of_child_projects,
            }
        )
        if parent_project_ref_id is not UNSET:
            field_dict["parent_project_ref_id"] = parent_project_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        order_of_child_projects = cast(list[str], d.pop("order_of_child_projects"))

        def _parse_parent_project_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_project_ref_id = _parse_parent_project_ref_id(d.pop("parent_project_ref_id", UNSET))

        project_summary = cls(
            ref_id=ref_id,
            name=name,
            order_of_child_projects=order_of_child_projects,
            parent_project_ref_id=parent_project_ref_id,
        )

        project_summary.additional_properties = d
        return project_summary

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
