from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ScheduleEventFullDaysCreateArgs")


@_attrs_define
class ScheduleEventFullDaysCreateArgs:
    """Args.

    Attributes:
        schedule_stream_ref_id (str): A generic entity id.
        name (str): The name of a schedule event.
        start_date (str): A date or possibly a datetime for the application.
        duration_days (int):
    """

    schedule_stream_ref_id: str
    name: str
    start_date: str
    duration_days: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schedule_stream_ref_id = self.schedule_stream_ref_id

        name = self.name

        start_date = self.start_date

        duration_days = self.duration_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedule_stream_ref_id": schedule_stream_ref_id,
                "name": name,
                "start_date": start_date,
                "duration_days": duration_days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        schedule_stream_ref_id = d.pop("schedule_stream_ref_id")

        name = d.pop("name")

        start_date = d.pop("start_date")

        duration_days = d.pop("duration_days")

        schedule_event_full_days_create_args = cls(
            schedule_stream_ref_id=schedule_stream_ref_id,
            name=name,
            start_date=start_date,
            duration_days=duration_days,
        )

        schedule_event_full_days_create_args.additional_properties = d
        return schedule_event_full_days_create_args

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
