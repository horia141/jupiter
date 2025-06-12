from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.big_plan_milestone import BigPlanMilestone


T = TypeVar("T", bound="BigPlanMilestoneCreateResult")


@_attrs_define
class BigPlanMilestoneCreateResult:
    """Big plan milestone create result.

    Attributes:
        new_big_plan_milestone (BigPlanMilestone): A milestone for tracking progress of a big plan.
    """

    new_big_plan_milestone: "BigPlanMilestone"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_big_plan_milestone = self.new_big_plan_milestone.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_big_plan_milestone": new_big_plan_milestone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.big_plan_milestone import BigPlanMilestone

        d = dict(src_dict)
        new_big_plan_milestone = BigPlanMilestone.from_dict(d.pop("new_big_plan_milestone"))

        big_plan_milestone_create_result = cls(
            new_big_plan_milestone=new_big_plan_milestone,
        )

        big_plan_milestone_create_result.additional_properties = d
        return big_plan_milestone_create_result

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
