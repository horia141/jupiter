from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocChangeParentArgs")


@_attrs_define
class DocChangeParentArgs:
    """DocChangeParent arguments.

    Attributes:
        ref_id (str): A generic entity id.
        parent_node_ref_id (Union[None, Unset, str]):
    """

    ref_id: str
    parent_node_ref_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        parent_node_ref_id: Union[None, Unset, str]
        if isinstance(self.parent_node_ref_id, Unset):
            parent_node_ref_id = UNSET
        else:
            parent_node_ref_id = self.parent_node_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
            }
        )
        if parent_node_ref_id is not UNSET:
            field_dict["parent_node_ref_id"] = parent_node_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        def _parse_parent_node_ref_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_node_ref_id = _parse_parent_node_ref_id(d.pop("parent_node_ref_id", UNSET))

        doc_change_parent_args = cls(
            ref_id=ref_id,
            parent_node_ref_id=parent_node_ref_id,
        )

        doc_change_parent_args.additional_properties = d
        return doc_change_parent_args

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
