from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.journal import Journal
    from ..models.note import Note


T = TypeVar("T", bound="JournalLoadResult")


@_attrs_define
class JournalLoadResult:
    """Result.

    Attributes:
        journal (Journal): A journal for a particular range.
        note (Note): A note in the notebook.
        sub_period_journals (List['Journal']):
        writing_task (Union['InboxTask', None, Unset]):
    """

    journal: "Journal"
    note: "Note"
    sub_period_journals: List["Journal"]
    writing_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.inbox_task import InboxTask

        journal = self.journal.to_dict()

        note = self.note.to_dict()

        sub_period_journals = []
        for sub_period_journals_item_data in self.sub_period_journals:
            sub_period_journals_item = sub_period_journals_item_data.to_dict()
            sub_period_journals.append(sub_period_journals_item)

        writing_task: Union[Dict[str, Any], None, Unset]
        if isinstance(self.writing_task, Unset):
            writing_task = UNSET
        elif isinstance(self.writing_task, InboxTask):
            writing_task = self.writing_task.to_dict()
        else:
            writing_task = self.writing_task

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "journal": journal,
                "note": note,
                "sub_period_journals": sub_period_journals,
            }
        )
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

        note = Note.from_dict(d.pop("note"))

        sub_period_journals = []
        _sub_period_journals = d.pop("sub_period_journals")
        for sub_period_journals_item_data in _sub_period_journals:
            sub_period_journals_item = Journal.from_dict(sub_period_journals_item_data)

            sub_period_journals.append(sub_period_journals_item)

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

        journal_load_result = cls(
            journal=journal,
            note=note,
            sub_period_journals=sub_period_journals,
            writing_task=writing_task,
        )

        journal_load_result.additional_properties = d
        return journal_load_result

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
