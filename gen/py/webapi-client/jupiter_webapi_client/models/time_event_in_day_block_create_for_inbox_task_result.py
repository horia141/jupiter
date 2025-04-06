from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_event_in_day_block import TimeEventInDayBlock


T = TypeVar("T", bound="TimeEventInDayBlockCreateForInboxTaskResult")


@_attrs_define
class TimeEventInDayBlockCreateForInboxTaskResult:
    """Result.

    Attributes:
        new_time_event (TimeEventInDayBlock): Time event.
    """

    new_time_event: "TimeEventInDayBlock"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_time_event = self.new_time_event.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_time_event": new_time_event,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_event_in_day_block import TimeEventInDayBlock

        d = dict(src_dict)
        new_time_event = TimeEventInDayBlock.from_dict(d.pop("new_time_event"))

        time_event_in_day_block_create_for_inbox_task_result = cls(
            new_time_event=new_time_event,
        )

        time_event_in_day_block_create_for_inbox_task_result.additional_properties = d
        return time_event_in_day_block_create_for_inbox_task_result

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
