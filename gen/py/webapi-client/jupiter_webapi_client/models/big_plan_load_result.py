from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan import BigPlan
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.project import Project


T = TypeVar("T", bound="BigPlanLoadResult")


@_attrs_define
class BigPlanLoadResult:
    """BigPlanLoadResult.

    Attributes:
        big_plan (BigPlan): A big plan.
        project (Project): The project.
        inbox_tasks (list['InboxTask']):
        note (Union['Note', None, Unset]):
    """

    big_plan: "BigPlan"
    project: "Project"
    inbox_tasks: list["InboxTask"]
    note: Union["Note", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.note import Note

        big_plan = self.big_plan.to_dict()

        project = self.project.to_dict()

        inbox_tasks = []
        for inbox_tasks_item_data in self.inbox_tasks:
            inbox_tasks_item = inbox_tasks_item_data.to_dict()
            inbox_tasks.append(inbox_tasks_item)

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
                "big_plan": big_plan,
                "project": project,
                "inbox_tasks": inbox_tasks,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan import BigPlan
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.project import Project

        d = dict(src_dict)
        big_plan = BigPlan.from_dict(d.pop("big_plan"))

        project = Project.from_dict(d.pop("project"))

        inbox_tasks = []
        _inbox_tasks = d.pop("inbox_tasks")
        for inbox_tasks_item_data in _inbox_tasks:
            inbox_tasks_item = InboxTask.from_dict(inbox_tasks_item_data)

            inbox_tasks.append(inbox_tasks_item)

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

        big_plan_load_result = cls(
            big_plan=big_plan,
            project=project,
            inbox_tasks=inbox_tasks,
            note=note,
        )

        big_plan_load_result.additional_properties = d
        return big_plan_load_result

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
