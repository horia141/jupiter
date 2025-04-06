from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.time_event_in_day_block_stats_per_group import TimeEventInDayBlockStatsPerGroup


T = TypeVar("T", bound="TimeEventInDayBlockStats")


@_attrs_define
class TimeEventInDayBlockStats:
    """Stats for time events.

    Attributes:
        per_groups (list['TimeEventInDayBlockStatsPerGroup']):
    """

    per_groups: list["TimeEventInDayBlockStatsPerGroup"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        per_groups = []
        for per_groups_item_data in self.per_groups:
            per_groups_item = per_groups_item_data.to_dict()
            per_groups.append(per_groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "per_groups": per_groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.time_event_in_day_block_stats_per_group import TimeEventInDayBlockStatsPerGroup

        d = dict(src_dict)
        per_groups = []
        _per_groups = d.pop("per_groups")
        for per_groups_item_data in _per_groups:
            per_groups_item = TimeEventInDayBlockStatsPerGroup.from_dict(per_groups_item_data)

            per_groups.append(per_groups_item)

        time_event_in_day_block_stats = cls(
            per_groups=per_groups,
        )

        time_event_in_day_block_stats.additional_properties = d
        return time_event_in_day_block_stats

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
