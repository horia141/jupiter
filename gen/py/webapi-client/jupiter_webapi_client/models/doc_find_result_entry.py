from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.doc import Doc
    from ..models.note import Note


T = TypeVar("T", bound="DocFindResultEntry")


@_attrs_define
class DocFindResultEntry:
    """A single entry in the load all docs response.

    Attributes:
        doc (Doc): A doc in the docbook.
        note (Union['Note', None, Unset]):
        subdocs (Union[None, Unset, list['Doc']]):
    """

    doc: "Doc"
    note: Union["Note", None, Unset] = UNSET
    subdocs: Union[None, Unset, list["Doc"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.note import Note

        doc = self.doc.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        subdocs: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.subdocs, Unset):
            subdocs = UNSET
        elif isinstance(self.subdocs, list):
            subdocs = []
            for subdocs_type_0_item_data in self.subdocs:
                subdocs_type_0_item = subdocs_type_0_item_data.to_dict()
                subdocs.append(subdocs_type_0_item)

        else:
            subdocs = self.subdocs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "doc": doc,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if subdocs is not UNSET:
            field_dict["subdocs"] = subdocs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc import Doc
        from ..models.note import Note

        d = dict(src_dict)
        doc = Doc.from_dict(d.pop("doc"))

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

        def _parse_subdocs(data: object) -> Union[None, Unset, list["Doc"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                subdocs_type_0 = []
                _subdocs_type_0 = data
                for subdocs_type_0_item_data in _subdocs_type_0:
                    subdocs_type_0_item = Doc.from_dict(subdocs_type_0_item_data)

                    subdocs_type_0.append(subdocs_type_0_item)

                return subdocs_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["Doc"]], data)

        subdocs = _parse_subdocs(d.pop("subdocs", UNSET))

        doc_find_result_entry = cls(
            doc=doc,
            note=note,
            subdocs=subdocs,
        )

        doc_find_result_entry.additional_properties = d
        return doc_find_result_entry

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
