from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_event_in_day_block_update_args_buffer_after_mins import (
        TimeEventInDayBlockUpdateArgsBufferAfterMins,
    )
    from ..models.time_event_in_day_block_update_args_buffer_before_mins import (
        TimeEventInDayBlockUpdateArgsBufferBeforeMins,
    )
    from ..models.time_event_in_day_block_update_args_duration_mins import TimeEventInDayBlockUpdateArgsDurationMins
    from ..models.time_event_in_day_block_update_args_start_date import TimeEventInDayBlockUpdateArgsStartDate
    from ..models.time_event_in_day_block_update_args_start_time_in_day import (
        TimeEventInDayBlockUpdateArgsStartTimeInDay,
    )


T = TypeVar("T", bound="TimeEventInDayBlockUpdateArgs")


@_attrs_define
class TimeEventInDayBlockUpdateArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        start_date (TimeEventInDayBlockUpdateArgsStartDate):
        start_time_in_day (TimeEventInDayBlockUpdateArgsStartTimeInDay):
        duration_mins (TimeEventInDayBlockUpdateArgsDurationMins):
        buffer_before_mins (TimeEventInDayBlockUpdateArgsBufferBeforeMins):
        buffer_after_mins (TimeEventInDayBlockUpdateArgsBufferAfterMins):
    """

    ref_id: str
    start_date: TimeEventInDayBlockUpdateArgsStartDate
    start_time_in_day: TimeEventInDayBlockUpdateArgsStartTimeInDay
    duration_mins: TimeEventInDayBlockUpdateArgsDurationMins
    buffer_before_mins: TimeEventInDayBlockUpdateArgsBufferBeforeMins
    buffer_after_mins: TimeEventInDayBlockUpdateArgsBufferAfterMins
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

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
        from ..models.time_event_in_day_block_update_args_buffer_after_mins import (
            TimeEventInDayBlockUpdateArgsBufferAfterMins,  # noqa: PLC0415
        )
        from ..models.time_event_in_day_block_update_args_buffer_before_mins import (
            TimeEventInDayBlockUpdateArgsBufferBeforeMins,  # noqa: PLC0415
        )
        from ..models.time_event_in_day_block_update_args_duration_mins import TimeEventInDayBlockUpdateArgsDurationMins  # noqa: PLC0415
        from ..models.time_event_in_day_block_update_args_start_date import TimeEventInDayBlockUpdateArgsStartDate  # noqa: PLC0415
        from ..models.time_event_in_day_block_update_args_start_time_in_day import (
            TimeEventInDayBlockUpdateArgsStartTimeInDay,  # noqa: PLC0415
        )

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        start_date = TimeEventInDayBlockUpdateArgsStartDate.from_dict(d.pop("start_date"))

        start_time_in_day = TimeEventInDayBlockUpdateArgsStartTimeInDay.from_dict(d.pop("start_time_in_day"))

        duration_mins = TimeEventInDayBlockUpdateArgsDurationMins.from_dict(d.pop("duration_mins"))

        buffer_before_mins = TimeEventInDayBlockUpdateArgsBufferBeforeMins.from_dict(d.pop("buffer_before_mins"))

        buffer_after_mins = TimeEventInDayBlockUpdateArgsBufferAfterMins.from_dict(d.pop("buffer_after_mins"))

        time_event_in_day_block_update_args = cls(
            ref_id=ref_id,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
            buffer_before_mins=buffer_before_mins,
            buffer_after_mins=buffer_after_mins,
        )

        time_event_in_day_block_update_args.additional_properties = d
        return time_event_in_day_block_update_args

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
