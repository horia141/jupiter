from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
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
    """

    ref_id: str
    start_date: "TimeEventInDayBlockUpdateArgsStartDate"
    start_time_in_day: "TimeEventInDayBlockUpdateArgsStartTimeInDay"
    duration_mins: "TimeEventInDayBlockUpdateArgsDurationMins"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        start_date = self.start_date.to_dict()

        start_time_in_day = self.start_time_in_day.to_dict()

        duration_mins = self.duration_mins.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "start_date": start_date,
                "start_time_in_day": start_time_in_day,
                "duration_mins": duration_mins,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.time_event_in_day_block_update_args_duration_mins import TimeEventInDayBlockUpdateArgsDurationMins
        from ..models.time_event_in_day_block_update_args_start_date import TimeEventInDayBlockUpdateArgsStartDate
        from ..models.time_event_in_day_block_update_args_start_time_in_day import (
            TimeEventInDayBlockUpdateArgsStartTimeInDay,
        )

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        start_date = TimeEventInDayBlockUpdateArgsStartDate.from_dict(d.pop("start_date"))

        start_time_in_day = TimeEventInDayBlockUpdateArgsStartTimeInDay.from_dict(d.pop("start_time_in_day"))

        duration_mins = TimeEventInDayBlockUpdateArgsDurationMins.from_dict(d.pop("duration_mins"))

        time_event_in_day_block_update_args = cls(
            ref_id=ref_id,
            start_date=start_date,
            start_time_in_day=start_time_in_day,
            duration_mins=duration_mins,
        )

        time_event_in_day_block_update_args.additional_properties = d
        return time_event_in_day_block_update_args

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