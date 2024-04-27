from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SmartListTagCreateArgs")


@_attrs_define
class SmartListTagCreateArgs:
    """SmartListTagCreate args.

    Attributes:
        smart_list_ref_id (str): A generic entity id.
        tag_name (str): The base value object for any kind of tag tag.
    """

    smart_list_ref_id: str
    tag_name: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        smart_list_ref_id = self.smart_list_ref_id

        tag_name = self.tag_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "smart_list_ref_id": smart_list_ref_id,
                "tag_name": tag_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        smart_list_ref_id = d.pop("smart_list_ref_id")

        tag_name = d.pop("tag_name")

        smart_list_tag_create_args = cls(
            smart_list_ref_id=smart_list_ref_id,
            tag_name=tag_name,
        )

        smart_list_tag_create_args.additional_properties = d
        return smart_list_tag_create_args

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
