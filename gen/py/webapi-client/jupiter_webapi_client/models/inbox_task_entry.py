from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.time_event_in_day_block import TimeEventInDayBlock


T = TypeVar("T", bound="InboxTaskEntry")


@_attrs_define
class InboxTaskEntry:
    """Result entry.

    Attributes:
        inbox_task (InboxTask): An inbox task.
        time_events (List['TimeEventInDayBlock']):
    """

    inbox_task: "InboxTask"
    time_events: List["TimeEventInDayBlock"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inbox_task = self.inbox_task.to_dict()

        time_events = []
        for time_events_item_data in self.time_events:
            time_events_item = time_events_item_data.to_dict()
            time_events.append(time_events_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbox_task": inbox_task,
                "time_events": time_events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.time_event_in_day_block import TimeEventInDayBlock

        d = src_dict.copy()
        inbox_task = InboxTask.from_dict(d.pop("inbox_task"))

        time_events = []
        _time_events = d.pop("time_events")
        for time_events_item_data in _time_events:
            time_events_item = TimeEventInDayBlock.from_dict(time_events_item_data)

            time_events.append(time_events_item)

        inbox_task_entry = cls(
            inbox_task=inbox_task,
            time_events=time_events,
        )

        inbox_task_entry.additional_properties = d
        return inbox_task_entry

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
