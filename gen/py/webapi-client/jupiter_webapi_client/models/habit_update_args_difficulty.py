from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.difficulty import Difficulty
from ..types import UNSET, Unset

T = TypeVar("T", bound="HabitUpdateArgsDifficulty")


@_attrs_define
class HabitUpdateArgsDifficulty:
    """
    Attributes:
        should_change (bool):
        value (Union[Unset, Difficulty]): The difficulty of a particular task.
    """

    should_change: bool
    value: Union[Unset, Difficulty] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        should_change = self.should_change

        value: Union[Unset, str] = UNSET
        if not isinstance(self.value, Unset):
            value = self.value.value

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        should_change = d.pop("should_change")

        _value = d.pop("value", UNSET)
        value: Union[Unset, Difficulty]
        if isinstance(_value, Unset):
            value = UNSET
        else:
            value = Difficulty(_value)

        habit_update_args_difficulty = cls(
            should_change=should_change,
            value=value,
        )

        habit_update_args_difficulty.additional_properties = d
        return habit_update_args_difficulty

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
