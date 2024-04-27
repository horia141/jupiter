from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.journal import Journal
    from ..models.note import Note


T = TypeVar("T", bound="JournalCreateResult")


@_attrs_define
class JournalCreateResult:
    """Result.

    Attributes:
        new_journal (Journal): A journal for a particular range.
        new_note (Note): A note in the notebook.
    """

    new_journal: "Journal"
    new_note: "Note"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_journal = self.new_journal.to_dict()

        new_note = self.new_note.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_journal": new_journal,
                "new_note": new_note,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.journal import Journal
        from ..models.note import Note

        d = src_dict.copy()
        new_journal = Journal.from_dict(d.pop("new_journal"))

        new_note = Note.from_dict(d.pop("new_note"))

        journal_create_result = cls(
            new_journal=new_journal,
            new_note=new_note,
        )

        journal_create_result.additional_properties = d
        return journal_create_result

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
