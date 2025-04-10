from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock
    from ..models.vacation import Vacation


T = TypeVar("T", bound="VacationCreateResult")


@_attrs_define
class VacationCreateResult:
    """Vacation creation result.

    Attributes:
        new_vacation (Vacation): A vacation.
        new_time_event_block (TimeEventFullDaysBlock): A full day block of time.
    """

    new_vacation: "Vacation"
    new_time_event_block: "TimeEventFullDaysBlock"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_vacation = self.new_vacation.to_dict()

        new_time_event_block = self.new_time_event_block.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_vacation": new_vacation,
                "new_time_event_block": new_time_event_block,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock
        from ..models.vacation import Vacation

        d = dict(src_dict)
        new_vacation = Vacation.from_dict(d.pop("new_vacation"))

        new_time_event_block = TimeEventFullDaysBlock.from_dict(d.pop("new_time_event_block"))

        vacation_create_result = cls(
            new_vacation=new_vacation,
            new_time_event_block=new_time_event_block,
        )

        vacation_create_result.additional_properties = d
        return vacation_create_result

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
