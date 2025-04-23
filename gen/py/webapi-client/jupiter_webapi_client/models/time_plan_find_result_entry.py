from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.note import Note
    from ..models.time_plan import TimePlan


T = TypeVar("T", bound="TimePlanFindResultEntry")


@_attrs_define
class TimePlanFindResultEntry:
    """Result part.

    Attributes:
        time_plan (TimePlan): A plan for a particular period of time.
        note (Union['Note', None, Unset]):
        planning_task (Union['InboxTask', None, Unset]):
    """

    time_plan: "TimePlan"
    note: Union["Note", None, Unset] = UNSET
    planning_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note

        time_plan = self.time_plan.to_dict()

        note: Union[None, Unset, dict[str, Any]]
        if isinstance(self.note, Unset):
            note = UNSET
        elif isinstance(self.note, Note):
            note = self.note.to_dict()
        else:
            note = self.note

        planning_task: Union[None, Unset, dict[str, Any]]
        if isinstance(self.planning_task, Unset):
            planning_task = UNSET
        elif isinstance(self.planning_task, InboxTask):
            planning_task = self.planning_task.to_dict()
        else:
            planning_task = self.planning_task

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time_plan": time_plan,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if planning_task is not UNSET:
            field_dict["planning_task"] = planning_task

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.note import Note
        from ..models.time_plan import TimePlan

        d = dict(src_dict)
        time_plan = TimePlan.from_dict(d.pop("time_plan"))

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

        def _parse_planning_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                planning_task_type_0 = InboxTask.from_dict(data)

                return planning_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        planning_task = _parse_planning_task(d.pop("planning_task", UNSET))

        time_plan_find_result_entry = cls(
            time_plan=time_plan,
            note=note,
            planning_task=planning_task,
        )

        time_plan_find_result_entry.additional_properties = d
        return time_plan_find_result_entry

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
