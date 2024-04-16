from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_tag import SmartListTag


T = TypeVar("T", bound="SmartListTagCreateResult")


@_attrs_define
class SmartListTagCreateResult:
    """SmartListTagCreate result.

    Attributes:
        new_smart_list_tag (SmartListTag): A smart list tag.
    """

    new_smart_list_tag: "SmartListTag"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_smart_list_tag = self.new_smart_list_tag.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_smart_list_tag": new_smart_list_tag,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.smart_list_tag import SmartListTag

        d = src_dict.copy()
        new_smart_list_tag = SmartListTag.from_dict(d.pop("new_smart_list_tag"))

        smart_list_tag_create_result = cls(
            new_smart_list_tag=new_smart_list_tag,
        )

        smart_list_tag_create_result.additional_properties = d
        return smart_list_tag_create_result

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
