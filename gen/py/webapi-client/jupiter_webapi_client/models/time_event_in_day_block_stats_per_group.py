from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_event_namespace import TimeEventNamespace

T = TypeVar("T", bound="TimeEventInDayBlockStatsPerGroup")


@_attrs_define
class TimeEventInDayBlockStatsPerGroup:
    """Just a slice of the stats.

    Attributes:
        date (str): A date or possibly a datetime for the application.
        namespace (TimeEventNamespace): Time event namespaces.
        cnt (int):
    """

    date: str
    namespace: TimeEventNamespace
    cnt: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        date = self.date

        namespace = self.namespace.value

        cnt = self.cnt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
                "namespace": namespace,
                "cnt": cnt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        date = d.pop("date")

        namespace = TimeEventNamespace(d.pop("namespace"))

        cnt = d.pop("cnt")

        time_event_in_day_block_stats_per_group = cls(
            date=date,
            namespace=namespace,
            cnt=cnt,
        )

        time_event_in_day_block_stats_per_group.additional_properties = d
        return time_event_in_day_block_stats_per_group

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
