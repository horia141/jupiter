from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.note import Note
    from ..models.smart_list import SmartList
    from ..models.smart_list_item import SmartListItem
    from ..models.smart_list_tag import SmartListTag


T = TypeVar("T", bound="SmartListFindResponseEntry")


@_attrs_define
class SmartListFindResponseEntry:
    """A single entry in the LoadAllSmartListsResponse.

    Attributes:
        smart_list (SmartList): A smart list.
        note (Union[Unset, Note]): A note in the notebook.
        smart_list_tags (Union[Unset, List['SmartListTag']]):
        smart_list_items (Union[Unset, List['SmartListItem']]):
        smart_list_item_notes (Union[Unset, List['Note']]):
    """

    smart_list: "SmartList"
    note: Union[Unset, "Note"] = UNSET
    smart_list_tags: Union[Unset, List["SmartListTag"]] = UNSET
    smart_list_items: Union[Unset, List["SmartListItem"]] = UNSET
    smart_list_item_notes: Union[Unset, List["Note"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        smart_list = self.smart_list.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        smart_list_tags: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.smart_list_tags, Unset):
            smart_list_tags = []
            for smart_list_tags_item_data in self.smart_list_tags:
                smart_list_tags_item = smart_list_tags_item_data.to_dict()
                smart_list_tags.append(smart_list_tags_item)

        smart_list_items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.smart_list_items, Unset):
            smart_list_items = []
            for smart_list_items_item_data in self.smart_list_items:
                smart_list_items_item = smart_list_items_item_data.to_dict()
                smart_list_items.append(smart_list_items_item)

        smart_list_item_notes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.smart_list_item_notes, Unset):
            smart_list_item_notes = []
            for smart_list_item_notes_item_data in self.smart_list_item_notes:
                smart_list_item_notes_item = smart_list_item_notes_item_data.to_dict()
                smart_list_item_notes.append(smart_list_item_notes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "smart_list": smart_list,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if smart_list_tags is not UNSET:
            field_dict["smart_list_tags"] = smart_list_tags
        if smart_list_items is not UNSET:
            field_dict["smart_list_items"] = smart_list_items
        if smart_list_item_notes is not UNSET:
            field_dict["smart_list_item_notes"] = smart_list_item_notes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.note import Note
        from ..models.smart_list import SmartList
        from ..models.smart_list_item import SmartListItem
        from ..models.smart_list_tag import SmartListTag

        d = src_dict.copy()
        smart_list = SmartList.from_dict(d.pop("smart_list"))

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        smart_list_tags = []
        _smart_list_tags = d.pop("smart_list_tags", UNSET)
        for smart_list_tags_item_data in _smart_list_tags or []:
            smart_list_tags_item = SmartListTag.from_dict(smart_list_tags_item_data)

            smart_list_tags.append(smart_list_tags_item)

        smart_list_items = []
        _smart_list_items = d.pop("smart_list_items", UNSET)
        for smart_list_items_item_data in _smart_list_items or []:
            smart_list_items_item = SmartListItem.from_dict(smart_list_items_item_data)

            smart_list_items.append(smart_list_items_item)

        smart_list_item_notes = []
        _smart_list_item_notes = d.pop("smart_list_item_notes", UNSET)
        for smart_list_item_notes_item_data in _smart_list_item_notes or []:
            smart_list_item_notes_item = Note.from_dict(smart_list_item_notes_item_data)

            smart_list_item_notes.append(smart_list_item_notes_item)

        smart_list_find_response_entry = cls(
            smart_list=smart_list,
            note=note,
            smart_list_tags=smart_list_tags,
            smart_list_items=smart_list_items,
            smart_list_item_notes=smart_list_item_notes,
        )

        smart_list_find_response_entry.additional_properties = d
        return smart_list_find_response_entry

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
