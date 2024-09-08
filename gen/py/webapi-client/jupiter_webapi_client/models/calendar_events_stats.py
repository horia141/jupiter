from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.recurring_task_period import RecurringTaskPeriod

if TYPE_CHECKING:
    from ..models.calendar_events_stats_per_subperiod import CalendarEventsStatsPerSubperiod


T = TypeVar("T", bound="CalendarEventsStats")


@_attrs_define
class CalendarEventsStats:
    """Stats about events in a period.

    Attributes:
        subperiod (RecurringTaskPeriod): A period for a particular task.
        per_subperiod (List['CalendarEventsStatsPerSubperiod']):
    """

    subperiod: RecurringTaskPeriod
    per_subperiod: List["CalendarEventsStatsPerSubperiod"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        subperiod = self.subperiod.value

        per_subperiod = []
        for per_subperiod_item_data in self.per_subperiod:
            per_subperiod_item = per_subperiod_item_data.to_dict()
            per_subperiod.append(per_subperiod_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subperiod": subperiod,
                "per_subperiod": per_subperiod,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.calendar_events_stats_per_subperiod import CalendarEventsStatsPerSubperiod

        d = src_dict.copy()
        subperiod = RecurringTaskPeriod(d.pop("subperiod"))

        per_subperiod = []
        _per_subperiod = d.pop("per_subperiod")
        for per_subperiod_item_data in _per_subperiod:
            per_subperiod_item = CalendarEventsStatsPerSubperiod.from_dict(per_subperiod_item_data)

            per_subperiod.append(per_subperiod_item)

        calendar_events_stats = cls(
            subperiod=subperiod,
            per_subperiod=per_subperiod,
        )

        calendar_events_stats.additional_properties = d
        return calendar_events_stats

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
