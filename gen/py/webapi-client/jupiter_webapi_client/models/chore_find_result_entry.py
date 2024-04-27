from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chore import Chore
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.project import Project


T = TypeVar("T", bound="ChoreFindResultEntry")


@_attrs_define
class ChoreFindResultEntry:
    """A single entry in the load all chores response.

    Attributes:
        chore (Chore): A chore.
        note (Union['Note', None, Unset]):
        project (Union['Project', None, Unset]):
        inbox_tasks (Union[List['InboxTask'], None, Unset]):
    """

    chore: "Chore"
    note: Union["Note", None, Unset] = UNSET
    project: Union["Project", None, Unset] = UNSET
    inbox_tasks: Union[List["InboxTask"], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.note import Note
        from ..models.project import Project

        chore = self.chore.to_dict()

        note: Union[Dict[str, Any], None, Unset]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        project: Union[Dict[str, Any], None, Unset]
        if isinstance(self.project, Unset):
            project = UNSET
        elif isinstance(self.project, Project):
            project = self.project.to_dict()
        else:
            project = self.project

        inbox_tasks: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.inbox_tasks, Unset):
            inbox_tasks = UNSET
        elif isinstance(self.inbox_tasks, list):
            inbox_tasks = []
            for inbox_tasks_type_0_item_data in self.inbox_tasks:
                inbox_tasks_type_0_item = inbox_tasks_type_0_item_data.to_dict()
                inbox_tasks.append(inbox_tasks_type_0_item)

        else:
            inbox_tasks = self.inbox_tasks

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chore": chore,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if project is not UNSET:
            field_dict["project"] = project
        if inbox_tasks is not UNSET:
            field_dict["inbox_tasks"] = inbox_tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.chore import Chore
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.project import Project

        d = src_dict.copy()
        chore = Chore.from_dict(d.pop("chore"))

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

        def _parse_project(data: object) -> Union["Project", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                project_type_0 = Project.from_dict(data)

                return project_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Project", None, Unset], data)

        project = _parse_project(d.pop("project", UNSET))

        def _parse_inbox_tasks(data: object) -> Union[List["InboxTask"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                inbox_tasks_type_0 = []
                _inbox_tasks_type_0 = data
                for inbox_tasks_type_0_item_data in _inbox_tasks_type_0:
                    inbox_tasks_type_0_item = InboxTask.from_dict(inbox_tasks_type_0_item_data)

                    inbox_tasks_type_0.append(inbox_tasks_type_0_item)

                return inbox_tasks_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["InboxTask"], None, Unset], data)

        inbox_tasks = _parse_inbox_tasks(d.pop("inbox_tasks", UNSET))

        chore_find_result_entry = cls(
            chore=chore,
            note=note,
            project=project,
            inbox_tasks=inbox_tasks,
        )

        chore_find_result_entry.additional_properties = d
        return chore_find_result_entry

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
