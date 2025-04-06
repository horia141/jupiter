from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_tag import SmartListTag


T = TypeVar("T", bound="SmartListTagLoadResult")


@_attrs_define
class SmartListTagLoadResult:
    """SmartListTagLoadResult.

    Attributes:
        smart_list_tag (SmartListTag): A smart list tag.
    """

    smart_list_tag: "SmartListTag"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        smart_list_tag = self.smart_list_tag.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "smart_list_tag": smart_list_tag,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.smart_list_tag import SmartListTag

        d = dict(src_dict)
        smart_list_tag = SmartListTag.from_dict(d.pop("smart_list_tag"))

        smart_list_tag_load_result = cls(
            smart_list_tag=smart_list_tag,
        )

        smart_list_tag_load_result.additional_properties = d
        return smart_list_tag_load_result

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
