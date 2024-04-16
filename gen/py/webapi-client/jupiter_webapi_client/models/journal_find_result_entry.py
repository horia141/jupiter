from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.journal import Journal
    from ..models.note import Note


T = TypeVar("T", bound="JournalFindResultEntry")


@_attrs_define
class JournalFindResultEntry:
    """Result part.

    Attributes:
        journal (Journal): A journal for a particular range.
        note (Union[Unset, Note]): A note in the notebook.
        writing_task (Union[Unset, InboxTask]): An inbox task.
    """

    journal: "Journal"
    note: Union[Unset, "Note"] = UNSET
    writing_task: Union[Unset, "InboxTask"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        journal = self.journal.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        writing_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.writing_task, Unset):
            writing_task = self.writing_task.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "journal": journal,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if writing_task is not UNSET:
            field_dict["writing_task"] = writing_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.journal import Journal
        from ..models.note import Note

        d = src_dict.copy()
        journal = Journal.from_dict(d.pop("journal"))

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        _writing_task = d.pop("writing_task", UNSET)
        writing_task: Union[Unset, InboxTask]
        if isinstance(_writing_task, Unset):
            writing_task = UNSET
        else:
            writing_task = InboxTask.from_dict(_writing_task)

        journal_find_result_entry = cls(
            journal=journal,
            note=note,
            writing_task=writing_task,
        )

        journal_find_result_entry.additional_properties = d
        return journal_find_result_entry

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
