from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ScheduleEventFullDaysChangeScheduleStreamArgs")


@_attrs_define
class ScheduleEventFullDaysChangeScheduleStreamArgs:
    """Args.

    Attributes:
        ref_id (str): A generic entity id.
        schedule_stream_ref_id (str): A generic entity id.
    """

    ref_id: str
    schedule_stream_ref_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        schedule_stream_ref_id = self.schedule_stream_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "schedule_stream_ref_id": schedule_stream_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        schedule_stream_ref_id = d.pop("schedule_stream_ref_id")

        schedule_event_full_days_change_schedule_stream_args = cls(
            ref_id=ref_id,
            schedule_stream_ref_id=schedule_stream_ref_id,
        )

        schedule_event_full_days_change_schedule_stream_args.additional_properties = d
        return schedule_event_full_days_change_schedule_stream_args

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
