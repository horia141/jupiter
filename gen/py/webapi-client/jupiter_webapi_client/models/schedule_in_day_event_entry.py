from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_event_in_day import ScheduleEventInDay
    from ..models.schedule_stream import ScheduleStream
    from ..models.time_event_in_day_block import TimeEventInDayBlock


T = TypeVar("T", bound="ScheduleInDayEventEntry")


@_attrs_define
class ScheduleInDayEventEntry:
    """Result entry.

    Attributes:
        event (ScheduleEventInDay): An event in a schedule.
        time_event (TimeEventInDayBlock): Time event.
        stream (ScheduleStream): A schedule group or stream of events.
    """

    event: "ScheduleEventInDay"
    time_event: "TimeEventInDayBlock"
    stream: "ScheduleStream"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        event = self.event.to_dict()

        time_event = self.time_event.to_dict()

        stream = self.stream.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event": event,
                "time_event": time_event,
                "stream": stream,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.schedule_event_in_day import ScheduleEventInDay
        from ..models.schedule_stream import ScheduleStream
        from ..models.time_event_in_day_block import TimeEventInDayBlock

        d = src_dict.copy()
        event = ScheduleEventInDay.from_dict(d.pop("event"))

        time_event = TimeEventInDayBlock.from_dict(d.pop("time_event"))

        stream = ScheduleStream.from_dict(d.pop("stream"))

        schedule_in_day_event_entry = cls(
            event=event,
            time_event=time_event,
            stream=stream,
        )

        schedule_in_day_event_entry.additional_properties = d
        return schedule_in_day_event_entry

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
