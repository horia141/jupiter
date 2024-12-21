from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProjectReorderChildrenArgs")


@_attrs_define
class ProjectReorderChildrenArgs:
    """Project reorder children args.

    Attributes:
        ref_id (str): A generic entity id.
        new_order_of_child_projects (List[str]):
    """

    ref_id: str
    new_order_of_child_projects: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        new_order_of_child_projects = self.new_order_of_child_projects

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "new_order_of_child_projects": new_order_of_child_projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        new_order_of_child_projects = cast(List[str], d.pop("new_order_of_child_projects"))

        project_reorder_children_args = cls(
            ref_id=ref_id,
            new_order_of_child_projects=new_order_of_child_projects,
        )

        project_reorder_children_args.additional_properties = d
        return project_reorder_children_args

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
