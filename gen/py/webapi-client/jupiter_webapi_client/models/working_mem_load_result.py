from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.working_mem import WorkingMem


T = TypeVar("T", bound="WorkingMemLoadResult")


@_attrs_define
class WorkingMemLoadResult:
    """Working mem load result.

    Attributes:
        working_mem (WorkingMem): An entry in the working_mem.txt system.
        note (Note): A note in the notebook.
        cleanup_tasks (list['InboxTask']):
        cleanup_tasks_total_cnt (int):
        cleanup_tasks_page_size (int):
    """

    working_mem: "WorkingMem"
    note: "Note"
    cleanup_tasks: list["InboxTask"]
    cleanup_tasks_total_cnt: int
    cleanup_tasks_page_size: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        working_mem = self.working_mem.to_dict()

        note = self.note.to_dict()

        cleanup_tasks = []
        for cleanup_tasks_item_data in self.cleanup_tasks:
            cleanup_tasks_item = cleanup_tasks_item_data.to_dict()
            cleanup_tasks.append(cleanup_tasks_item)

        cleanup_tasks_total_cnt = self.cleanup_tasks_total_cnt

        cleanup_tasks_page_size = self.cleanup_tasks_page_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "working_mem": working_mem,
                "note": note,
                "cleanup_tasks": cleanup_tasks,
                "cleanup_tasks_total_cnt": cleanup_tasks_total_cnt,
                "cleanup_tasks_page_size": cleanup_tasks_page_size,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.working_mem import WorkingMem

        d = dict(src_dict)
        working_mem = WorkingMem.from_dict(d.pop("working_mem"))

        note = Note.from_dict(d.pop("note"))

        cleanup_tasks = []
        _cleanup_tasks = d.pop("cleanup_tasks")
        for cleanup_tasks_item_data in _cleanup_tasks:
            cleanup_tasks_item = InboxTask.from_dict(cleanup_tasks_item_data)

            cleanup_tasks.append(cleanup_tasks_item)

        cleanup_tasks_total_cnt = d.pop("cleanup_tasks_total_cnt")

        cleanup_tasks_page_size = d.pop("cleanup_tasks_page_size")

        working_mem_load_result = cls(
            working_mem=working_mem,
            note=note,
            cleanup_tasks=cleanup_tasks,
            cleanup_tasks_total_cnt=cleanup_tasks_total_cnt,
            cleanup_tasks_page_size=cleanup_tasks_page_size,
        )

        working_mem_load_result.additional_properties = d
        return working_mem_load_result

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
