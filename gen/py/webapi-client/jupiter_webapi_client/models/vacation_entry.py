from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock
    from ..models.vacation import Vacation


T = TypeVar("T", bound="VacationEntry")


@_attrs_define
class VacationEntry:
    """Result entry.

    Attributes:
        vacation (Vacation): A vacation.
        time_event (TimeEventFullDaysBlock): A full day block of time.
    """

    vacation: "Vacation"
    time_event: "TimeEventFullDaysBlock"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vacation = self.vacation.to_dict()

        time_event = self.time_event.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vacation": vacation,
                "time_event": time_event,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock
        from ..models.vacation import Vacation

        d = dict(src_dict)
        vacation = Vacation.from_dict(d.pop("vacation"))

        time_event = TimeEventFullDaysBlock.from_dict(d.pop("time_event"))

        vacation_entry = cls(
            vacation=vacation,
            time_event=time_event,
        )

        vacation_entry.additional_properties = d
        return vacation_entry

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
