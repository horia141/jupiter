from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_stream import ScheduleStream


T = TypeVar("T", bound="ScheduleStreamCreateForUserResult")


@_attrs_define
class ScheduleStreamCreateForUserResult:
    """Result.

    Attributes:
        new_schedule_stream (ScheduleStream): A schedule group or stream of events.
    """

    new_schedule_stream: "ScheduleStream"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        new_schedule_stream = self.new_schedule_stream.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_schedule_stream": new_schedule_stream,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.schedule_stream import ScheduleStream

        d = src_dict.copy()
        new_schedule_stream = ScheduleStream.from_dict(d.pop("new_schedule_stream"))

        schedule_stream_create_for_user_result = cls(
            new_schedule_stream=new_schedule_stream,
        )

        schedule_stream_create_for_user_result.additional_properties = d
        return schedule_stream_create_for_user_result

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
