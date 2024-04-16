from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkableBigPlan")


@_attrs_define
class WorkableBigPlan:
    """The view of a big plan via a workable.

    Attributes:
        ref_id (str): A generic entity id.
        name (str): The big plan name.
        actionable_date (Union[Unset, str]): A date or possibly a datetime for the application.
    """

    ref_id: str
    name: str
    actionable_date: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        name = self.name

        actionable_date = self.actionable_date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
            }
        )
        if actionable_date is not UNSET:
            field_dict["actionable_date"] = actionable_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        name = d.pop("name")

        actionable_date = d.pop("actionable_date", UNSET)

        workable_big_plan = cls(
            ref_id=ref_id,
            name=name,
            actionable_date=actionable_date,
        )

        workable_big_plan.additional_properties = d
        return workable_big_plan

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
