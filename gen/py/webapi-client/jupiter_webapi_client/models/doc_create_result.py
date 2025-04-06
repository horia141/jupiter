from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.doc import Doc
    from ..models.note import Note


T = TypeVar("T", bound="DocCreateResult")


@_attrs_define
class DocCreateResult:
    """DocCreate result.

    Attributes:
        new_doc (Doc): A doc in the docbook.
        new_note (Note): A note in the notebook.
    """

    new_doc: "Doc"
    new_note: "Note"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_doc = self.new_doc.to_dict()

        new_note = self.new_note.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_doc": new_doc,
                "new_note": new_note,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc import Doc
        from ..models.note import Note

        d = dict(src_dict)
        new_doc = Doc.from_dict(d.pop("new_doc"))

        new_note = Note.from_dict(d.pop("new_note"))

        doc_create_result = cls(
            new_doc=new_doc,
            new_note=new_note,
        )

        doc_create_result.additional_properties = d
        return doc_create_result

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
