from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.habit_streak_mark_statuses import HabitStreakMarkStatuses


T = TypeVar("T", bound="HabitStreakMark")


@_attrs_define
class HabitStreakMark:
    """The record of a streak of a habit.

    Attributes:
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        habit_ref_id (str):
        year (int):
        date (str): A date or possibly a datetime for the application.
        statuses (HabitStreakMarkStatuses):
    """

    created_time: str
    last_modified_time: str
    habit_ref_id: str
    year: int
    date: str
    statuses: "HabitStreakMarkStatuses"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_time = self.created_time

        last_modified_time = self.last_modified_time

        habit_ref_id = self.habit_ref_id

        year = self.year

        date = self.date

        statuses = self.statuses.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "habit_ref_id": habit_ref_id,
                "year": year,
                "date": date,
                "statuses": statuses,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.habit_streak_mark_statuses import HabitStreakMarkStatuses

        d = dict(src_dict)
        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        habit_ref_id = d.pop("habit_ref_id")

        year = d.pop("year")

        date = d.pop("date")

        statuses = HabitStreakMarkStatuses.from_dict(d.pop("statuses"))

        habit_streak_mark = cls(
            created_time=created_time,
            last_modified_time=last_modified_time,
            habit_ref_id=habit_ref_id,
            year=year,
            date=date,
            statuses=statuses,
        )

        habit_streak_mark.additional_properties = d
        return habit_streak_mark

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
