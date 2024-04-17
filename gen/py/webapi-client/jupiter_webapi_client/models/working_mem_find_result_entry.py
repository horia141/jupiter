from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.working_mem import WorkingMem


T = TypeVar("T", bound="WorkingMemFindResultEntry")


@_attrs_define
class WorkingMemFindResultEntry:
    """PersonFindResult object.

    Attributes:
        working_mem (WorkingMem): An entry in the working_mem.txt system.
        note (Union['Note', None, Unset]):
        cleanup_task (Union['InboxTask', None, Unset]):
    """

    working_mem: "WorkingMem"
    note: Union["Note", None, Unset] = UNSET
    cleanup_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note

        working_mem = self.working_mem.to_dict()

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        cleanup_task: Union[Dict[str, Any], None, Unset]
        if isinstance(self.cleanup_task, Unset):
            cleanup_task = UNSET
        elif isinstance(self.cleanup_task, InboxTask):
            cleanup_task = self.cleanup_task.to_dict()
        else:
            cleanup_task = self.cleanup_task

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "working_mem": working_mem,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if cleanup_task is not UNSET:
            field_dict["cleanup_task"] = cleanup_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.working_mem import WorkingMem

        d = src_dict.copy()
        working_mem = WorkingMem.from_dict(d.pop("working_mem"))

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

        def _parse_cleanup_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cleanup_task_type_0 = InboxTask.from_dict(data)

                return cleanup_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        cleanup_task = _parse_cleanup_task(d.pop("cleanup_task", UNSET))

        working_mem_find_result_entry = cls(
            working_mem=working_mem,
            note=note,
            cleanup_task=cleanup_task,
        )

        working_mem_find_result_entry.additional_properties = d
        return working_mem_find_result_entry

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
