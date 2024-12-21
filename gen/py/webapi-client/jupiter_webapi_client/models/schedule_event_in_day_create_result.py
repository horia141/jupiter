from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_event_in_day import ScheduleEventInDay
    from ..models.time_event_in_day_block import TimeEventInDayBlock


T = TypeVar("T", bound="ScheduleEventInDayCreateResult")


@_attrs_define
class ScheduleEventInDayCreateResult:
    """Result.

    Attributes:
        new_schedule_event_in_day (ScheduleEventInDay): An event in a schedule.
        new_time_event_in_day_block (TimeEventInDayBlock): Time event.
    """

    new_schedule_event_in_day: "ScheduleEventInDay"
    new_time_event_in_day_block: "TimeEventInDayBlock"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_schedule_event_in_day = self.new_schedule_event_in_day.to_dict()

        new_time_event_in_day_block = self.new_time_event_in_day_block.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_schedule_event_in_day": new_schedule_event_in_day,
                "new_time_event_in_day_block": new_time_event_in_day_block,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.schedule_event_in_day import ScheduleEventInDay
        from ..models.time_event_in_day_block import TimeEventInDayBlock

        d = src_dict.copy()
        new_schedule_event_in_day = ScheduleEventInDay.from_dict(d.pop("new_schedule_event_in_day"))

        new_time_event_in_day_block = TimeEventInDayBlock.from_dict(d.pop("new_time_event_in_day_block"))

        schedule_event_in_day_create_result = cls(
            new_schedule_event_in_day=new_schedule_event_in_day,
            new_time_event_in_day_block=new_time_event_in_day_block,
        )

        schedule_event_in_day_create_result.additional_properties = d
        return schedule_event_in_day_create_result

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
