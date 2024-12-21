from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schedule_source import ScheduleSource
from ..models.schedule_stream_color import ScheduleStreamColor

T = TypeVar("T", bound="ScheduleStreamSummary")


@_attrs_define
class ScheduleStreamSummary:
    """Summary information about a schedule stream.

    Attributes:
        ref_id (str): A generic entity id.
        source (ScheduleSource): The source of a schedule.
        name (str): The name of a schedule stream.
        color (ScheduleStreamColor): The color of a particular schedule stream.
    """

    ref_id: str
    source: ScheduleSource
    name: str
    color: ScheduleStreamColor
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        source = self.source.value

        name = self.name

        color = self.color.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "source": source,
                "name": name,
                "color": color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        source = ScheduleSource(d.pop("source"))

        name = d.pop("name")

        color = ScheduleStreamColor(d.pop("color"))

        schedule_stream_summary = cls(
            ref_id=ref_id,
            source=source,
            name=name,
            color=color,
        )

        schedule_stream_summary.additional_properties = d
        return schedule_stream_summary

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
