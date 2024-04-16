from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

if TYPE_CHECKING:
    from ..models.recurring_task_work_summary import RecurringTaskWorkSummary


T = TypeVar("T", bound="PerChoreBreakdownItem")


@_attrs_define
class PerChoreBreakdownItem:
    """The report for a particular chore.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The name for an entity which acts as both name and unique identifier.
        suspended (bool):
        archived (bool):
        period (RecurringTaskPeriod): A period for a particular task.
        summary (RecurringTaskWorkSummary): The reporting summary.
    """

    ref_id: str
    name: str
    suspended: bool
    archived: bool
    period: RecurringTaskPeriod
    summary: "RecurringTaskWorkSummary"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        suspended = self.suspended

        archived = self.archived

        period = self.period.value

        summary = self.summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "suspended": suspended,
                "archived": archived,
                "period": period,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.recurring_task_work_summary import RecurringTaskWorkSummary

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        suspended = d.pop("suspended")

        archived = d.pop("archived")

        period = RecurringTaskPeriod(d.pop("period"))

        summary = RecurringTaskWorkSummary.from_dict(d.pop("summary"))

        per_chore_breakdown_item = cls(
            ref_id=ref_id,
            name=name,
            suspended=suspended,
            archived=archived,
            period=period,
            summary=summary,
        )

        per_chore_breakdown_item.additional_properties = d
        return per_chore_breakdown_item

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
