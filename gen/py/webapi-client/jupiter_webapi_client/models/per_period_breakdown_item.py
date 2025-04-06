from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_tasks_summary import InboxTasksSummary
    from ..models.workable_summary import WorkableSummary


T = TypeVar("T", bound="PerPeriodBreakdownItem")


@_attrs_define
class PerPeriodBreakdownItem:
    """The report for a particular time period.

    Attributes:
        name (str): The name for an entity which acts as both name and unique identifier.
        inbox_tasks_summary (InboxTasksSummary): A bigger summary for inbox tasks.
        big_plans_summary (WorkableSummary): The reporting summary.
    """

    name: str
    inbox_tasks_summary: "InboxTasksSummary"
    big_plans_summary: "WorkableSummary"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        inbox_tasks_summary = self.inbox_tasks_summary.to_dict()

        big_plans_summary = self.big_plans_summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "inbox_tasks_summary": inbox_tasks_summary,
                "big_plans_summary": big_plans_summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.inbox_tasks_summary import InboxTasksSummary
        from ..models.workable_summary import WorkableSummary

        d = dict(src_dict)
        name = d.pop("name")

        inbox_tasks_summary = InboxTasksSummary.from_dict(d.pop("inbox_tasks_summary"))

        big_plans_summary = WorkableSummary.from_dict(d.pop("big_plans_summary"))

        per_period_breakdown_item = cls(
            name=name,
            inbox_tasks_summary=inbox_tasks_summary,
            big_plans_summary=big_plans_summary,
        )

        per_period_breakdown_item.additional_properties = d
        return per_period_breakdown_item

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
