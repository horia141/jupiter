from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        note (Union[Unset, Note]): A note in the notebook.
        cleanup_task (Union[Unset, InboxTask]): An inbox task.
    """

    working_mem: "WorkingMem"
    note: Union[Unset, "Note"] = UNSET
    cleanup_task: Union[Unset, "InboxTask"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        working_mem = self.working_mem.to_dict()

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        cleanup_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cleanup_task, Unset):
            cleanup_task = self.cleanup_task.to_dict()

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

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        _cleanup_task = d.pop("cleanup_task", UNSET)
        cleanup_task: Union[Unset, InboxTask]
        if isinstance(_cleanup_task, Unset):
            cleanup_task = UNSET
        else:
            cleanup_task = InboxTask.from_dict(_cleanup_task)

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
