from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.smart_list_find_response_entry import SmartListFindResponseEntry


T = TypeVar("T", bound="SmartListFindResult")


@_attrs_define
class SmartListFindResult:
    """PersonFindResult object.

    Attributes:
        entries (list['SmartListFindResponseEntry']):
    """

    entries: list["SmartListFindResponseEntry"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.smart_list_find_response_entry import SmartListFindResponseEntry

        d = dict(src_dict)
        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = SmartListFindResponseEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        smart_list_find_result = cls(
            entries=entries,
        )

        smart_list_find_result.additional_properties = d
        return smart_list_find_result

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
