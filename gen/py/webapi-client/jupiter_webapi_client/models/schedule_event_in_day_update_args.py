from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_event_in_day_update_args_buffer_after_mins import ScheduleEventInDayUpdateArgsBufferAfterMins
    from ..models.schedule_event_in_day_update_args_buffer_before_mins import (
        ScheduleEventInDayUpdateArgsBufferBeforeMins,
    )
    from ..models.schedule_event_in_day_update_args_duration_mins import ScheduleEventInDayUpdateArgsDurationMins
    from ..models.schedule_event_in_day_update_args_name import ScheduleEventInDayUpdateArgsName
    from ..models.schedule_event_in_day_update_args_start_date import ScheduleEventInDayUpdateArgsStartDate
    from ..models.schedule_event_in_day_update_args_start_time_in_day import ScheduleEventInDayUpdateArgsStartTimeInDay


T = TypeVar("T", bound="ScheduleEventInDayUpdateArgs")


@_attrs_define
class ScheduleEventInDayUpdateArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        name (ScheduleEventInDayUpdateArgsName):
        start_date (ScheduleEventInDayUpdateArgsStartDate):
        start_time_in_day (ScheduleEventInDayUpdateArgsStartTimeInDay):
        duration_mins (ScheduleEventInDayUpdateArgsDurationMins):
        buffer_before_mins (ScheduleEventInDayUpdateArgsBufferBeforeMins):
        buffer_after_mins (ScheduleEventInDayUpdateArgsBufferAfterMins):
    """

    ref_id: str
    name: ScheduleEventInDayUpdateArgsName
    start_date: ScheduleEventInDayUpdateArgsStartDate
    start_time_in_day: ScheduleEventInDayUpdateArgsStartTimeInDay
    duration_mins: ScheduleEventInDayUpdateArgsDurationMins
    buffer_before_mins: ScheduleEventInDayUpdateArgsBufferBeforeMins
    buffer_after_mins: ScheduleEventInDayUpdateArgsBufferAfterMins
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        name = self.name.to_dict()

        start_date = self.start_date.to_dict()

        start_time_in_day = self.start_time_in_day.to_dict()

        duration_mins = self.duration_mins.to_dict()

        buffer_before_mins = self.buffer_before_mins.to_dict()

        buffer_after_mins = self.buffer_after_mins.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "name": name,
                "start_date": start_date,
                "start_time_in_day": start_time_in_day,
                "duration_mins": duration_mins,
                "buffer_before_mins": buffer_before_mins,
                "buffer_after_mins": buffer_after_mins,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schedule_event_in_day_update_args_buffer_after_mins import (
            ScheduleEventInDayUpdateArgsBufferAfterMins,  # noqa: PLC0415
        )
        from ..models.schedule_event_in_day_update_args_buffer_before_mins import (
            ScheduleEventInDayUpdateArgsBufferBeforeMins,  # noqa: PLC0415
        )
        from ..models.schedule_event_in_day_update_args_duration_mins import ScheduleEventInDayUpdateArgsDurationMins  # noqa: PLC0415
        from ..models.schedule_event_in_day_update_args_name import ScheduleEventInDayUpdateArgsName  # noqa: PLC0415
        from ..models.schedule_event_in_day_update_args_start_date import ScheduleEventInDayUpdateArgsStartDate  # noqa: PLC0415
        from ..models.schedule_event_in_day_update_args_start_time_in_day import (
            ScheduleEventInDayUpdateArgsStartTimeInDay,  # noqa: PLC0415
        )

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        name = ScheduleEventInDayUpdateArgsName.from_dict(d.pop("name"))

        start_date = ScheduleEventInDayUpdateArgsStartDate.from_dict(d.pop("start_date"))

        start_time_in_day = ScheduleEventInDayUpdateArgsStartTimeInDay.from_dict(d.pop("start_time_in_day"))

        duration_mins = ScheduleEventInDayUpdateArgsDurationMins.from_dict(d.pop("duration_mins"))

        buffer_before_mins = ScheduleEventInDayUpdateArgsBufferBeforeMins.from_dict(d.pop("buffer_before_mins"))

        buffer_after_mins = ScheduleEventInDayUpdateArgsBufferAfterMins.from_dict(d.pop("buffer_after_mins"))

        schedule_event_in_day_update_args = cls(
            ref_id=ref_id,
            name=name,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
            buffer_before_mins=buffer_before_mins,
            buffer_after_mins=buffer_after_mins,
        )

        schedule_event_in_day_update_args.additional_properties = d
        return schedule_event_in_day_update_args

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
