from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TimeEventInDayBlockCreateForInboxTaskArgs")


@_attrs_define
class TimeEventInDayBlockCreateForInboxTaskArgs:
    """Args.

    Attributes:
        inbox_task_ref_id (str): A generic entity id.
        start_date (str): A date or possibly a datetime for the application.
        start_time_in_day (str): The time in hh:mm format.
        duration_mins (int):
    """

    inbox_task_ref_id: str
    start_date: str
    start_time_in_day: str
    duration_mins: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inbox_task_ref_id = self.inbox_task_ref_id

        start_date = self.start_date

        start_time_in_day = self.start_time_in_day

        duration_mins = self.duration_mins

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inbox_task_ref_id": inbox_task_ref_id,
                "start_date": start_date,
                "start_time_in_day": start_time_in_day,
                "duration_mins": duration_mins,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        inbox_task_ref_id = d.pop("inbox_task_ref_id")

        start_date = d.pop("start_date")

        start_time_in_day = d.pop("start_time_in_day")

        duration_mins = d.pop("duration_mins")

        time_event_in_day_block_create_for_inbox_task_args = cls(
            inbox_task_ref_id=inbox_task_ref_id,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
        )

        time_event_in_day_block_create_for_inbox_task_args.additional_properties = d
        return time_event_in_day_block_create_for_inbox_task_args

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
