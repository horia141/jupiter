from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChoreUpdateArgsPeriod")


@_attrs_define
class ChoreUpdateArgsPeriod:
    """
    Attributes:
        should_change (bool):
        value (Union[Unset, RecurringTaskPeriod]): A period for a particular task.
    """

    should_change: bool
    value: Union[Unset, RecurringTaskPeriod] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        should_change = self.should_change

        value: Union[Unset, str] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "should_change": should_change,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        should_change = d.pop("should_change")

        _value = d.pop("value", UNSET)
        value: Union[Unset, RecurringTaskPeriod]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = RecurringTaskPeriod(_value)

        chore_update_args_period = cls(
            should_change=should_change,
            value=value,
        )

        chore_update_args_period.additional_properties = d
        return chore_update_args_period

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
