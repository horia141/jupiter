from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_event_full_days import ScheduleEventFullDays
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock


T = TypeVar("T", bound="ScheduleEventFullDaysCreateResult")


@_attrs_define
class ScheduleEventFullDaysCreateResult:
    """Result.

    Attributes:
        new_schedule_event_full_days (ScheduleEventFullDays): A full day block in a schedule.
        new_time_event_full_day_block (TimeEventFullDaysBlock): A full day block of time.
    """

    new_schedule_event_full_days: "ScheduleEventFullDays"
    new_time_event_full_day_block: "TimeEventFullDaysBlock"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_schedule_event_full_days = self.new_schedule_event_full_days.to_dict()

        new_time_event_full_day_block = self.new_time_event_full_day_block.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_schedule_event_full_days": new_schedule_event_full_days,
                "new_time_event_full_day_block": new_time_event_full_day_block,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock

        d = src_dict.copy()
        new_schedule_event_full_days = ScheduleEventFullDays.from_dict(d.pop("new_schedule_event_full_days"))

        new_time_event_full_day_block = TimeEventFullDaysBlock.from_dict(d.pop("new_time_event_full_day_block"))

        schedule_event_full_days_create_result = cls(
            new_schedule_event_full_days=new_schedule_event_full_days,
            new_time_event_full_day_block=new_time_event_full_day_block,
        )

        schedule_event_full_days_create_result.additional_properties = d
        return schedule_event_full_days_create_result

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
