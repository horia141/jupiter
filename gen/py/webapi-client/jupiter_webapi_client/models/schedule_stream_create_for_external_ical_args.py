from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schedule_stream_color import ScheduleStreamColor

T = TypeVar("T", bound="ScheduleStreamCreateForExternalIcalArgs")


@_attrs_define
class ScheduleStreamCreateForExternalIcalArgs:
    """Args.

    Attributes:
        source_ical_url (str): A URL in this domain.
        color (ScheduleStreamColor): The color of a particular schedule stream.
    """

    source_ical_url: str
    color: ScheduleStreamColor
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source_ical_url = self.source_ical_url

        color = self.color.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_ical_url": source_ical_url,
                "color": color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source_ical_url = d.pop("source_ical_url")

        color = ScheduleStreamColor(d.pop("color"))

        schedule_stream_create_for_external_ical_args = cls(
            source_ical_url=source_ical_url,
            color=color,
        )

        schedule_stream_create_for_external_ical_args.additional_properties = d
        return schedule_stream_create_for_external_ical_args

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
