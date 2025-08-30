from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.habit import Habit
    from ..models.habit_streak_mark import HabitStreakMark
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.project import Project


T = TypeVar("T", bound="HabitLoadResult")


@_attrs_define
class HabitLoadResult:
    """HabitLoadResult.

    Attributes:
        habit (Habit): A habit.
        project (Project): The project.
        inbox_tasks (list['InboxTask']):
        inbox_tasks_total_cnt (int):
        inbox_tasks_page_size (int):
        streak_marks (list['HabitStreakMark']):
        streak_mark_earliest_date (str): A date or possibly a datetime for the application.
        streak_mark_latest_date (str): A date or possibly a datetime for the application.
        note (Union['Note', None, Unset]):
    """

    habit: "Habit"
    project: "Project"
    inbox_tasks: list["InboxTask"]
    inbox_tasks_total_cnt: int
    inbox_tasks_page_size: int
    streak_marks: list["HabitStreakMark"]
    streak_mark_earliest_date: str
    streak_mark_latest_date: str
    note: Union["Note", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.note import Note

        habit = self.habit.to_dict()

        project = self.project.to_dict()

        inbox_tasks = []
        for inbox_tasks_item_data in self.inbox_tasks:
            inbox_tasks_item = inbox_tasks_item_data.to_dict()
            inbox_tasks.append(inbox_tasks_item)

        inbox_tasks_total_cnt = self.inbox_tasks_total_cnt

        inbox_tasks_page_size = self.inbox_tasks_page_size

        streak_marks = []
        for streak_marks_item_data in self.streak_marks:
            streak_marks_item = streak_marks_item_data.to_dict()
            streak_marks.append(streak_marks_item)

        streak_mark_earliest_date = self.streak_mark_earliest_date

        streak_mark_latest_date = self.streak_mark_latest_date

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "habit": habit,
                "project": project,
                "inbox_tasks": inbox_tasks,
                "inbox_tasks_total_cnt": inbox_tasks_total_cnt,
                "inbox_tasks_page_size": inbox_tasks_page_size,
                "streak_marks": streak_marks,
                "streak_mark_earliest_date": streak_mark_earliest_date,
                "streak_mark_latest_date": streak_mark_latest_date,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.habit import Habit
        from ..models.habit_streak_mark import HabitStreakMark
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.project import Project

        d = dict(src_dict)
        habit = Habit.from_dict(d.pop("habit"))

        project = Project.from_dict(d.pop("project"))

        inbox_tasks = []
        _inbox_tasks = d.pop("inbox_tasks")
        for inbox_tasks_item_data in _inbox_tasks:
            inbox_tasks_item = InboxTask.from_dict(inbox_tasks_item_data)

            inbox_tasks.append(inbox_tasks_item)

        inbox_tasks_total_cnt = d.pop("inbox_tasks_total_cnt")

        inbox_tasks_page_size = d.pop("inbox_tasks_page_size")

        streak_marks = []
        _streak_marks = d.pop("streak_marks")
        for streak_marks_item_data in _streak_marks:
            streak_marks_item = HabitStreakMark.from_dict(streak_marks_item_data)

            streak_marks.append(streak_marks_item)

        streak_mark_earliest_date = d.pop("streak_mark_earliest_date")

        streak_mark_latest_date = d.pop("streak_mark_latest_date")

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

        habit_load_result = cls(
            habit=habit,
            project=project,
            inbox_tasks=inbox_tasks,
            inbox_tasks_total_cnt=inbox_tasks_total_cnt,
            inbox_tasks_page_size=inbox_tasks_page_size,
            streak_marks=streak_marks,
            streak_mark_earliest_date=streak_mark_earliest_date,
            streak_mark_latest_date=streak_mark_latest_date,
            note=note,
        )

        habit_load_result.additional_properties = d
        return habit_load_result

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
