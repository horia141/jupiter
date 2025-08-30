from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.big_plan_milestone_update_args_date import BigPlanMilestoneUpdateArgsDate
    from ..models.big_plan_milestone_update_args_name import BigPlanMilestoneUpdateArgsName


T = TypeVar("T", bound="BigPlanMilestoneUpdateArgs")


@_attrs_define
class BigPlanMilestoneUpdateArgs:
    """Big plan milestone update args.

    Attributes:
        ref_id (str): A generic entity id.
        date (BigPlanMilestoneUpdateArgsDate):
        name (BigPlanMilestoneUpdateArgsName):
    """

    ref_id: str
    date: "BigPlanMilestoneUpdateArgsDate"
    name: "BigPlanMilestoneUpdateArgsName"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        date = self.date.to_dict()

        name = self.name.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "date": date,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan_milestone_update_args_date import BigPlanMilestoneUpdateArgsDate
        from ..models.big_plan_milestone_update_args_name import BigPlanMilestoneUpdateArgsName

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        date = BigPlanMilestoneUpdateArgsDate.from_dict(d.pop("date"))

        name = BigPlanMilestoneUpdateArgsName.from_dict(d.pop("name"))

        big_plan_milestone_update_args = cls(
            ref_id=ref_id,
            date=date,
            name=name,
        )

        big_plan_milestone_update_args.additional_properties = d
        return big_plan_milestone_update_args

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
