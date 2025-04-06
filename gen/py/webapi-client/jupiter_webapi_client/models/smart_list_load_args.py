from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SmartListLoadArgs")


@_attrs_define
class SmartListLoadArgs:
    """SmartListLoadArgs.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        allow_archived_items (bool):
        allow_archived_tags (bool):
    """

    ref_id: str
    allow_archived: bool
    allow_archived_items: bool
    allow_archived_tags: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        allow_archived_items = self.allow_archived_items

        allow_archived_tags = self.allow_archived_tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
                "allow_archived_items": allow_archived_items,
                "allow_archived_tags": allow_archived_tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        allow_archived_items = d.pop("allow_archived_items")

        allow_archived_tags = d.pop("allow_archived_tags")

        smart_list_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            allow_archived_items=allow_archived_items,
            allow_archived_tags=allow_archived_tags,
        )

        smart_list_load_args.additional_properties = d
        return smart_list_load_args

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
