from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_event_namespace import TimeEventNamespace

T = TypeVar("T", bound="TimeEventFullDaysBlockStatsPerGroup")


@_attrs_define
class TimeEventFullDaysBlockStatsPerGroup:
    """Just a slice of the stats.

    Attributes:
        date (str): A date or possibly a datetime for the application.
        namespace (TimeEventNamespace): Time event namespaces.
        cnt (int):
    """

    date: str
    namespace: TimeEventNamespace
    cnt: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        namespace = self.namespace.value

        cnt = self.cnt

        field_dict: dict[str, Any] = {}
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
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = d.pop("date")

        namespace = TimeEventNamespace(d.pop("namespace"))

        cnt = d.pop("cnt")

        time_event_full_days_block_stats_per_group = cls(
            date=date,
            namespace=namespace,
            cnt=cnt,
        )

        time_event_full_days_block_stats_per_group.additional_properties = d
        return time_event_full_days_block_stats_per_group

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
