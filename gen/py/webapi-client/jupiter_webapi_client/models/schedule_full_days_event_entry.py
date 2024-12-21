from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_event_full_days import ScheduleEventFullDays
    from ..models.schedule_stream import ScheduleStream
    from ..models.time_event_full_days_block import TimeEventFullDaysBlock


T = TypeVar("T", bound="ScheduleFullDaysEventEntry")


@_attrs_define
class ScheduleFullDaysEventEntry:
    """Result entry.

    Attributes:
        event (ScheduleEventFullDays): A full day block in a schedule.
        time_event (TimeEventFullDaysBlock): A full day block of time.
        stream (ScheduleStream): A schedule group or stream of events.
    """

    event: "ScheduleEventFullDays"
    time_event: "TimeEventFullDaysBlock"
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
        from ..models.schedule_event_full_days import ScheduleEventFullDays
        from ..models.schedule_stream import ScheduleStream
        from ..models.time_event_full_days_block import TimeEventFullDaysBlock

        d = src_dict.copy()
        event = ScheduleEventFullDays.from_dict(d.pop("event"))

        time_event = TimeEventFullDaysBlock.from_dict(d.pop("time_event"))

        stream = ScheduleStream.from_dict(d.pop("stream"))

        schedule_full_days_event_entry = cls(
            event=event,
            time_event=time_event,
            stream=stream,
        )

        schedule_full_days_event_entry.additional_properties = d
        return schedule_full_days_event_entry

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
