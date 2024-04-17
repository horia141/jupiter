from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.note import Note
    from ..models.smart_list import SmartList
    from ..models.smart_list_item import SmartListItem
    from ..models.smart_list_tag import SmartListTag


T = TypeVar("T", bound="SmartListLoadResult")


@_attrs_define
class SmartListLoadResult:
    """SmartListLoadResult.

    Attributes:
        smart_list (SmartList): A smart list.
        smart_list_tags (List['SmartListTag']):
        smart_list_items (List['SmartListItem']):
        smart_list_item_notes (List['Note']):
        note (Union['Note', None, Unset]):
    """

    smart_list: "SmartList"
    smart_list_tags: List["SmartListTag"]
    smart_list_items: List["SmartListItem"]
    smart_list_item_notes: List["Note"]
    note: Union["Note", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.note import Note

        smart_list = self.smart_list.to_dict()

        smart_list_tags = []
        for smart_list_tags_item_data in self.smart_list_tags:
            smart_list_tags_item = smart_list_tags_item_data.to_dict()
            smart_list_tags.append(smart_list_tags_item)

        smart_list_items = []
        for smart_list_items_item_data in self.smart_list_items:
            smart_list_items_item = smart_list_items_item_data.to_dict()
            smart_list_items.append(smart_list_items_item)

        smart_list_item_notes = []
        for smart_list_item_notes_item_data in self.smart_list_item_notes:
            smart_list_item_notes_item = smart_list_item_notes_item_data.to_dict()
            smart_list_item_notes.append(smart_list_item_notes_item)

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "smart_list": smart_list,
                "smart_list_tags": smart_list_tags,
                "smart_list_items": smart_list_items,
                "smart_list_item_notes": smart_list_item_notes,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.note import Note
        from ..models.smart_list import SmartList
        from ..models.smart_list_item import SmartListItem
        from ..models.smart_list_tag import SmartListTag

        d = src_dict.copy()
        smart_list = SmartList.from_dict(d.pop("smart_list"))

        smart_list_tags = []
        _smart_list_tags = d.pop("smart_list_tags")
        for smart_list_tags_item_data in _smart_list_tags:
            smart_list_tags_item = SmartListTag.from_dict(smart_list_tags_item_data)

            smart_list_tags.append(smart_list_tags_item)

        smart_list_items = []
        _smart_list_items = d.pop("smart_list_items")
        for smart_list_items_item_data in _smart_list_items:
            smart_list_items_item = SmartListItem.from_dict(smart_list_items_item_data)

            smart_list_items.append(smart_list_items_item)

        smart_list_item_notes = []
        _smart_list_item_notes = d.pop("smart_list_item_notes")
        for smart_list_item_notes_item_data in _smart_list_item_notes:
            smart_list_item_notes_item = Note.from_dict(smart_list_item_notes_item_data)

            smart_list_item_notes.append(smart_list_item_notes_item)

        def _parse_note(data: object) -> Union["Note", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                note_type_0 = Note.from_dict(data)

                return note_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Note", None, Unset], data)

        note = _parse_note(d.pop("note", UNSET))

        smart_list_load_result = cls(
            smart_list=smart_list,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
            smart_list_item_notes=smart_list_item_notes,
            note=note,
        )

        smart_list_load_result.additional_properties = d
        return smart_list_load_result

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
