from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.habit import Habit
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.project import Project


T = TypeVar("T", bound="HabitFindResultEntry")


@_attrs_define
class HabitFindResultEntry:
    """A single entry in the load all habits response.

    Attributes:
        habit (Habit): A habit.
        project (Union[Unset, Project]): The project.
        inbox_tasks (Union[Unset, List['InboxTask']]):
        note (Union[Unset, Note]): A note in the notebook.
    """

    habit: "Habit"
    project: Union[Unset, "Project"] = UNSET
    inbox_tasks: Union[Unset, List["InboxTask"]] = UNSET
    note: Union[Unset, "Note"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        habit = self.habit.to_dict()

        project: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.project, Unset):
            project = self.project.to_dict()

        inbox_tasks: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.inbox_tasks, Unset):
            inbox_tasks = []
            for inbox_tasks_item_data in self.inbox_tasks:
                inbox_tasks_item = inbox_tasks_item_data.to_dict()
                inbox_tasks.append(inbox_tasks_item)

        note: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.note, Unset):
            note = self.note.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "habit": habit,
            }
        )
        if project is not UNSET:
            field_dict["project"] = project
        if inbox_tasks is not UNSET:
            field_dict["inbox_tasks"] = inbox_tasks
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.habit import Habit
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.project import Project

        d = src_dict.copy()
        habit = Habit.from_dict(d.pop("habit"))

        _project = d.pop("project", UNSET)
        project: Union[Unset, Project]
        if isinstance(_project, Unset):
            project = UNSET
        else:
            project = Project.from_dict(_project)

        inbox_tasks = []
        _inbox_tasks = d.pop("inbox_tasks", UNSET)
        for inbox_tasks_item_data in _inbox_tasks or []:
            inbox_tasks_item = InboxTask.from_dict(inbox_tasks_item_data)

            inbox_tasks.append(inbox_tasks_item)

        _note = d.pop("note", UNSET)
        note: Union[Unset, Note]
        if isinstance(_note, Unset):
            note = UNSET
        else:
            note = Note.from_dict(_note)

        habit_find_result_entry = cls(
            habit=habit,
            project=project,
            inbox_tasks=inbox_tasks,
            note=note,
        )

        habit_find_result_entry.additional_properties = d
        return habit_find_result_entry

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
