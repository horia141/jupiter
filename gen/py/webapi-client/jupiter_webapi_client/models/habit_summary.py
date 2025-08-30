from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

T = TypeVar("T", bound="HabitSummary")


@_attrs_define
class HabitSummary:
    """Summary information about a habit.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The habit name.
        is_key (bool):
        period (RecurringTaskPeriod): A period for a particular task.
        project_ref_id (str): A generic entity id.
    """

    ref_id: str
    name: str
    is_key: bool
    period: RecurringTaskPeriod
    project_ref_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        is_key = self.is_key

        period = self.period.value

        project_ref_id = self.project_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "is_key": is_key,
                "period": period,
                "project_ref_id": project_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        is_key = d.pop("is_key")

        period = RecurringTaskPeriod(d.pop("period"))

        project_ref_id = d.pop("project_ref_id")

        habit_summary = cls(
            ref_id=ref_id,
            name=name,
            is_key=is_key,
            period=period,
            project_ref_id=project_ref_id,
        )

        habit_summary.additional_properties = d
        return habit_summary

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
