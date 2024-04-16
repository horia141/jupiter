from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_tag_update_args_tag_name import SmartListTagUpdateArgsTagName


T = TypeVar("T", bound="SmartListTagUpdateArgs")


@_attrs_define
class SmartListTagUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        tag_name (SmartListTagUpdateArgsTagName):
    """

    ref_id: str
    tag_name: "SmartListTagUpdateArgsTagName"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        tag_name = self.tag_name.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "tag_name": tag_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.smart_list_tag_update_args_tag_name import SmartListTagUpdateArgsTagName

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        tag_name = SmartListTagUpdateArgsTagName.from_dict(d.pop("tag_name"))

        smart_list_tag_update_args = cls(
            ref_id=ref_id,
            tag_name=tag_name,
        )

        smart_list_tag_update_args.additional_properties = d
        return smart_list_tag_update_args

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
