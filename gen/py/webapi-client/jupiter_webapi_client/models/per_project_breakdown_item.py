from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_tasks_summary import InboxTasksSummary
    from ..models.workable_summary import WorkableSummary


T = TypeVar("T", bound="PerProjectBreakdownItem")


@_attrs_define
class PerProjectBreakdownItem:
    """The report for a particular project.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The name for an entity which acts as both name and unique identifier.
        inbox_tasks_summary (InboxTasksSummary): A bigger summary for inbox tasks.
        big_plans_summary (WorkableSummary): The reporting summary.
    """

    ref_id: str
    name: str
    inbox_tasks_summary: "InboxTasksSummary"
    big_plans_summary: "WorkableSummary"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        inbox_tasks_summary = self.inbox_tasks_summary.to_dict()

        big_plans_summary = self.big_plans_summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "inbox_tasks_summary": inbox_tasks_summary,
                "big_plans_summary": big_plans_summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_tasks_summary import InboxTasksSummary
        from ..models.workable_summary import WorkableSummary

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        inbox_tasks_summary = InboxTasksSummary.from_dict(d.pop("inbox_tasks_summary"))

        big_plans_summary = WorkableSummary.from_dict(d.pop("big_plans_summary"))

        per_project_breakdown_item = cls(
            ref_id=ref_id,
            name=name,
            inbox_tasks_summary=inbox_tasks_summary,
            big_plans_summary=big_plans_summary,
        )

        per_project_breakdown_item.additional_properties = d
        return per_project_breakdown_item

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
