from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.note_update_args_content import NoteUpdateArgsContent


T = TypeVar("T", bound="NoteUpdateArgs")


@_attrs_define
class NoteUpdateArgs:
    """NoteUpdate args.

    Attributes:
        ref_id (str): A generic entity id.
        content (NoteUpdateArgsContent):
    """

    ref_id: str
    content: "NoteUpdateArgsContent"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        content = self.content.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "content": content,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.note_update_args_content import NoteUpdateArgsContent

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        content = NoteUpdateArgsContent.from_dict(d.pop("content"))

        note_update_args = cls(
            ref_id=ref_id,
            content=content,
        )

        note_update_args.additional_properties = d
        return note_update_args

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
