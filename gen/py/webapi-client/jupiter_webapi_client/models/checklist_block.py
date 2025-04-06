from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.checklist_block_kind import ChecklistBlockKind

if TYPE_CHECKING:
    from ..models.checklist_item import ChecklistItem


T = TypeVar("T", bound="ChecklistBlock")


@_attrs_define
class ChecklistBlock:
    """A todo list.

    Attributes:
        correlation_id (str): A generic entity id.
        kind (ChecklistBlockKind):
        items (list['ChecklistItem']):
    """

    correlation_id: str
    kind: ChecklistBlockKind
    items: list["ChecklistItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        correlation_id = self.correlation_id

        kind = self.kind.value

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "kind": kind,
                "items": items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.checklist_item import ChecklistItem

        d = dict(src_dict)
        correlation_id = d.pop("correlation_id")

        kind = ChecklistBlockKind(d.pop("kind"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = ChecklistItem.from_dict(items_item_data)

            items.append(items_item)

        checklist_block = cls(
            correlation_id=correlation_id,
            kind=kind,
            items=items,
        )

        checklist_block.additional_properties = d
        return checklist_block

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
