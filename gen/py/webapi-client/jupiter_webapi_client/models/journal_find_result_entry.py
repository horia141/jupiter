from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

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
        note (Union['Note', None, Unset]):
        writing_task (Union['InboxTask', None, Unset]):
    """

    journal: "Journal"
    note: Union["Note", None, Unset] = UNSET
    writing_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note

        journal = self.journal.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        writing_task: Union[None, Unset, dict[str, Any]]
        if isinstance(self.writing_task, Unset):
            writing_task = UNSET
        elif isinstance(self.writing_task, InboxTask):
            writing_task = self.writing_task.to_dict()
        else:
            writing_task = self.writing_task

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.journal import Journal
        from ..models.note import Note

        d = dict(src_dict)
        journal = Journal.from_dict(d.pop("journal"))

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

        def _parse_writing_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                writing_task_type_0 = InboxTask.from_dict(data)

                return writing_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        writing_task = _parse_writing_task(d.pop("writing_task", UNSET))

        journal_find_result_entry = cls(
            journal=journal,
            note=note,
            writing_task=writing_task,
        )

        journal_find_result_entry.additional_properties = d
        return journal_find_result_entry

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
