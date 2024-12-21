from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.doc import Doc
    from ..models.note import Note


T = TypeVar("T", bound="DocLoadResult")


@_attrs_define
class DocLoadResult:
    """DocLoad result.

    Attributes:
        doc (Doc): A doc in the docbook.
        note (Note): A note in the notebook.
        subdocs (List['Doc']):
    """

    doc: "Doc"
    note: "Note"
    subdocs: List["Doc"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        doc = self.doc.to_dict()

        note = self.note.to_dict()

        subdocs = []
        for subdocs_item_data in self.subdocs:
            subdocs_item = subdocs_item_data.to_dict()
            subdocs.append(subdocs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "doc": doc,
                "note": note,
                "subdocs": subdocs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.doc import Doc
        from ..models.note import Note

        d = src_dict.copy()
        doc = Doc.from_dict(d.pop("doc"))

        note = Note.from_dict(d.pop("note"))

        subdocs = []
        _subdocs = d.pop("subdocs")
        for subdocs_item_data in _subdocs:
            subdocs_item = Doc.from_dict(subdocs_item_data)

            subdocs.append(subdocs_item)

        doc_load_result = cls(
            doc=doc,
            note=note,
            subdocs=subdocs,
        )

        doc_load_result.additional_properties = d
        return doc_load_result

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
