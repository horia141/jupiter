from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.inbox_task import InboxTask
    from ..models.schedule_event_in_day import ScheduleEventInDay
    from ..models.time_event_in_day_block import TimeEventInDayBlock


T = TypeVar("T", bound="TimeEventInDayBlockLoadResult")


@_attrs_define
class TimeEventInDayBlockLoadResult:
    """InDayBlockLoadResult.

    Attributes:
        in_day_block (TimeEventInDayBlock): Time event.
        schedule_event (Union['ScheduleEventInDay', None, Unset]):
        inbox_task (Union['InboxTask', None, Unset]):
    """

    in_day_block: "TimeEventInDayBlock"
    schedule_event: Union["ScheduleEventInDay", None, Unset] = UNSET
    inbox_task: Union["InboxTask", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.inbox_task import InboxTask
        from ..models.schedule_event_in_day import ScheduleEventInDay

        in_day_block = self.in_day_block.to_dict()

        schedule_event: Union[Dict[str, Any], None, Unset]
        if isinstance(self.schedule_event, Unset):
            schedule_event = UNSET
        elif isinstance(self.schedule_event, ScheduleEventInDay):
            schedule_event = self.schedule_event.to_dict()
        else:
            schedule_event = self.schedule_event

        inbox_task: Union[Dict[str, Any], None, Unset]
        if isinstance(self.inbox_task, Unset):
            inbox_task = UNSET
        elif isinstance(self.inbox_task, InboxTask):
            inbox_task = self.inbox_task.to_dict()
        else:
            inbox_task = self.inbox_task

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "in_day_block": in_day_block,
            }
        )
        if schedule_event is not UNSET:
            field_dict["schedule_event"] = schedule_event
        if inbox_task is not UNSET:
            field_dict["inbox_task"] = inbox_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.inbox_task import InboxTask
        from ..models.schedule_event_in_day import ScheduleEventInDay
        from ..models.time_event_in_day_block import TimeEventInDayBlock

        d = src_dict.copy()
        in_day_block = TimeEventInDayBlock.from_dict(d.pop("in_day_block"))

        def _parse_schedule_event(data: object) -> Union["ScheduleEventInDay", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schedule_event_type_0 = ScheduleEventInDay.from_dict(data)

                return schedule_event_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ScheduleEventInDay", None, Unset], data)

        schedule_event = _parse_schedule_event(d.pop("schedule_event", UNSET))

        def _parse_inbox_task(data: object) -> Union["InboxTask", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                inbox_task_type_0 = InboxTask.from_dict(data)

                return inbox_task_type_0
            except:  # noqa: E722
                pass
            return cast(Union["InboxTask", None, Unset], data)

        inbox_task = _parse_inbox_task(d.pop("inbox_task", UNSET))

        time_event_in_day_block_load_result = cls(
            in_day_block=in_day_block,
            schedule_event=schedule_event,
            inbox_task=inbox_task,
        )

        time_event_in_day_block_load_result.additional_properties = d
        return time_event_in_day_block_load_result

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
