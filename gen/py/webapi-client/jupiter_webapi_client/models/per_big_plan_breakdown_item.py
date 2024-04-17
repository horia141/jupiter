from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.big_plan_work_summary import BigPlanWorkSummary


T = TypeVar("T", bound="PerBigPlanBreakdownItem")


@_attrs_define
class PerBigPlanBreakdownItem:
    """The report for a particular big plan.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The name for an entity which acts as both name and unique identifier.
        summary (BigPlanWorkSummary): The report for a big plan.
        actionable_date (Union[None, Unset, str]):
    """

    ref_id: str
    name: str
    summary: "BigPlanWorkSummary"
    actionable_date: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        summary = self.summary.to_dict()

        actionable_date: Union[None, Unset, str]
        if isinstance(self.actionable_date, Unset):
            actionable_date = UNSET
        else:
            actionable_date = self.actionable_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "summary": summary,
            }
        )
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.big_plan_work_summary import BigPlanWorkSummary

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        summary = BigPlanWorkSummary.from_dict(d.pop("summary"))

        def _parse_actionable_date(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        actionable_date = _parse_actionable_date(d.pop("actionable_date", UNSET))

        per_big_plan_breakdown_item = cls(
            ref_id=ref_id,
            name=name,
            summary=summary,
            actionable_date=actionable_date,
        )

        per_big_plan_breakdown_item.additional_properties = d
        return per_big_plan_breakdown_item

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
