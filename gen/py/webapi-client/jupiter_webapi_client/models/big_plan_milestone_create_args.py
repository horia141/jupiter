from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BigPlanMilestoneCreateArgs")


@_attrs_define
class BigPlanMilestoneCreateArgs:
    """Big plan milestone create args.

    Attributes:
        big_plan_ref_id (str): A generic entity id.
        date (str): A date or possibly a datetime for the application.
        name (str): The name for an entity which acts as both name and unique identifier.
    """

    big_plan_ref_id: str
    date: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        big_plan_ref_id = self.big_plan_ref_id

        date = self.date

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "big_plan_ref_id": big_plan_ref_id,
                "date": date,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        big_plan_ref_id = d.pop("big_plan_ref_id")

        date = d.pop("date")

        name = d.pop("name")

        big_plan_milestone_create_args = cls(
            big_plan_ref_id=big_plan_ref_id,
            date=date,
            name=name,
        )

        big_plan_milestone_create_args.additional_properties = d
        return big_plan_milestone_create_args

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
