from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        note (Union[Unset, Note]): A note in the notebook.
        subdocs (Union[Unset, List['Doc']]):
    """

    doc: "Doc"
    note: Union[Unset, "Note"] = UNSET
    subdocs: Union[Unset, List["Doc"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        doc = self.doc.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        subdocs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.subdocs, Unset):
            subdocs = []
            for subdocs_item_data in self.subdocs:
                subdocs_item = subdocs_item_data.to_dict()
                subdocs.append(subdocs_item)

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.doc import Doc
        from ..models.note import Note

        d = src_dict.copy()
        doc = Doc.from_dict(d.pop("doc"))

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        subdocs = []
        _subdocs = d.pop("subdocs", UNSET)
        for subdocs_item_data in _subdocs or []:
            subdocs_item = Doc.from_dict(subdocs_item_data)

            subdocs.append(subdocs_item)

        doc_find_result_entry = cls(
            doc=doc,
            note=note,
            subdocs=subdocs,
        )

        doc_find_result_entry.additional_properties = d
        return doc_find_result_entry

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
