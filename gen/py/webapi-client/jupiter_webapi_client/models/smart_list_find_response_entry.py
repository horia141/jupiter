from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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
        note (Union['Note', None, Unset]):
        smart_list_tags (Union[None, Unset, list['SmartListTag']]):
        smart_list_items (Union[None, Unset, list['SmartListItem']]):
        smart_list_item_notes (Union[None, Unset, list['Note']]):
    """

    smart_list: "SmartList"
    note: Union["Note", None, Unset] = UNSET
    smart_list_tags: Union[None, Unset, list["SmartListTag"]] = UNSET
    smart_list_items: Union[None, Unset, list["SmartListItem"]] = UNSET
    smart_list_item_notes: Union[None, Unset, list["Note"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.note import Note

        smart_list = self.smart_list.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        smart_list_tags: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.smart_list_tags, Unset):
            smart_list_tags = UNSET
        elif isinstance(self.smart_list_tags, list):
            smart_list_tags = []
            for smart_list_tags_type_0_item_data in self.smart_list_tags:
                smart_list_tags_type_0_item = smart_list_tags_type_0_item_data.to_dict()
                smart_list_tags.append(smart_list_tags_type_0_item)

        else:
            smart_list_tags = self.smart_list_tags

        smart_list_items: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.smart_list_items, Unset):
            smart_list_items = UNSET
        elif isinstance(self.smart_list_items, list):
            smart_list_items = []
            for smart_list_items_type_0_item_data in self.smart_list_items:
                smart_list_items_type_0_item = smart_list_items_type_0_item_data.to_dict()
                smart_list_items.append(smart_list_items_type_0_item)

        else:
            smart_list_items = self.smart_list_items

        smart_list_item_notes: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.smart_list_item_notes, Unset):
            smart_list_item_notes = UNSET
        elif isinstance(self.smart_list_item_notes, list):
            smart_list_item_notes = []
            for smart_list_item_notes_type_0_item_data in self.smart_list_item_notes:
                smart_list_item_notes_type_0_item = smart_list_item_notes_type_0_item_data.to_dict()
                smart_list_item_notes.append(smart_list_item_notes_type_0_item)

        else:
            smart_list_item_notes = self.smart_list_item_notes

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.note import Note
        from ..models.smart_list import SmartList
        from ..models.smart_list_item import SmartListItem
        from ..models.smart_list_tag import SmartListTag

        d = dict(src_dict)
        smart_list = SmartList.from_dict(d.pop("smart_list"))

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

        def _parse_smart_list_tags(data: object) -> Union[None, Unset, list["SmartListTag"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                smart_list_tags_type_0 = []
                _smart_list_tags_type_0 = data
                for smart_list_tags_type_0_item_data in _smart_list_tags_type_0:
                    smart_list_tags_type_0_item = SmartListTag.from_dict(smart_list_tags_type_0_item_data)

                    smart_list_tags_type_0.append(smart_list_tags_type_0_item)

                return smart_list_tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["SmartListTag"]], data)

        smart_list_tags = _parse_smart_list_tags(d.pop("smart_list_tags", UNSET))

        def _parse_smart_list_items(data: object) -> Union[None, Unset, list["SmartListItem"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                smart_list_items_type_0 = []
                _smart_list_items_type_0 = data
                for smart_list_items_type_0_item_data in _smart_list_items_type_0:
                    smart_list_items_type_0_item = SmartListItem.from_dict(smart_list_items_type_0_item_data)

                    smart_list_items_type_0.append(smart_list_items_type_0_item)

                return smart_list_items_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["SmartListItem"]], data)

        smart_list_items = _parse_smart_list_items(d.pop("smart_list_items", UNSET))

        def _parse_smart_list_item_notes(data: object) -> Union[None, Unset, list["Note"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                smart_list_item_notes_type_0 = []
                _smart_list_item_notes_type_0 = data
                for smart_list_item_notes_type_0_item_data in _smart_list_item_notes_type_0:
                    smart_list_item_notes_type_0_item = Note.from_dict(smart_list_item_notes_type_0_item_data)

                    smart_list_item_notes_type_0.append(smart_list_item_notes_type_0_item)

                return smart_list_item_notes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["Note"]], data)

        smart_list_item_notes = _parse_smart_list_item_notes(d.pop("smart_list_item_notes", UNSET))

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
