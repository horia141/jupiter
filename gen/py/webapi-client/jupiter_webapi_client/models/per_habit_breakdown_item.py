from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

if TYPE_CHECKING:
    from ..models.recurring_task_work_summary import RecurringTaskWorkSummary


T = TypeVar("T", bound="PerHabitBreakdownItem")


@_attrs_define
class PerHabitBreakdownItem:
    """The report for a particular habit.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The name for an entity which acts as both name and unique identifier.
        archived (bool):
        period (RecurringTaskPeriod): A period for a particular task.
        suspended (bool):
        summary (RecurringTaskWorkSummary): The reporting summary.
    """

    ref_id: str
    name: str
    archived: bool
    period: RecurringTaskPeriod
    suspended: bool
    summary: "RecurringTaskWorkSummary"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        archived = self.archived

        period = self.period.value

        suspended = self.suspended

        summary = self.summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "archived": archived,
                "period": period,
                "suspended": suspended,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recurring_task_work_summary import RecurringTaskWorkSummary

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        archived = d.pop("archived")

        period = RecurringTaskPeriod(d.pop("period"))

        suspended = d.pop("suspended")

        summary = RecurringTaskWorkSummary.from_dict(d.pop("summary"))

        per_habit_breakdown_item = cls(
            ref_id=ref_id,
            name=name,
            archived=archived,
            period=period,
            suspended=suspended,
            summary=summary,
        )

        per_habit_breakdown_item.additional_properties = d
        return per_habit_breakdown_item

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
