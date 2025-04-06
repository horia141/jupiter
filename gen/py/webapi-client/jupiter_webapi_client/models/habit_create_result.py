from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.habit import Habit


T = TypeVar("T", bound="HabitCreateResult")


@_attrs_define
class HabitCreateResult:
    """HabitCreate result.

    Attributes:
        new_habit (Habit): A habit.
    """

    new_habit: "Habit"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_habit = self.new_habit.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_habit": new_habit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.habit import Habit

        d = dict(src_dict)
        new_habit = Habit.from_dict(d.pop("new_habit"))

        habit_create_result = cls(
            new_habit=new_habit,
        )

        habit_create_result.additional_properties = d
        return habit_create_result

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
