from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SmartListTagLoadArgs")


@_attrs_define
class SmartListTagLoadArgs:
    """SmartListTagLoadArgs.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
    """

    ref_id: str
    allow_archived: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        smart_list_tag_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
        )

        smart_list_tag_load_args.additional_properties = d
        return smart_list_tag_load_args

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
