from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.note import Note
    from ..models.smart_list_item import SmartListItem
    from ..models.smart_list_tag import SmartListTag


T = TypeVar("T", bound="SmartListItemLoadResult")


@_attrs_define
class SmartListItemLoadResult:
    """SmartListItemLoadResult.

    Attributes:
        item (SmartListItem): A smart list item.
        tags (List['SmartListTag']):
        note (Union[Unset, Note]): A note in the notebook.
    """

    item: "SmartListItem"
    tags: List["SmartListTag"]
    note: Union[Unset, "Note"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        item = self.item.to_dict()

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "item": item,
                "tags": tags,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.note import Note
        from ..models.smart_list_item import SmartListItem
        from ..models.smart_list_tag import SmartListTag

        d = src_dict.copy()
        item = SmartListItem.from_dict(d.pop("item"))

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = SmartListTag.from_dict(tags_item_data)

            tags.append(tags_item)

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        smart_list_item_load_result = cls(
            item=item,
            tags=tags,
            note=note,
        )

        smart_list_item_load_result.additional_properties = d
        return smart_list_item_load_result

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
