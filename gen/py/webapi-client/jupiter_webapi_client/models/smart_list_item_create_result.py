from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_item import SmartListItem


T = TypeVar("T", bound="SmartListItemCreateResult")


@_attrs_define
class SmartListItemCreateResult:
    """SmartListItemCreate result.

    Attributes:
        new_smart_list_item (SmartListItem): A smart list item.
    """

    new_smart_list_item: "SmartListItem"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_smart_list_item = self.new_smart_list_item.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_smart_list_item": new_smart_list_item,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.smart_list_item import SmartListItem

        d = src_dict.copy()
        new_smart_list_item = SmartListItem.from_dict(d.pop("new_smart_list_item"))

        smart_list_item_create_result = cls(
            new_smart_list_item=new_smart_list_item,
        )

        smart_list_item_create_result.additional_properties = d
        return smart_list_item_create_result

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
