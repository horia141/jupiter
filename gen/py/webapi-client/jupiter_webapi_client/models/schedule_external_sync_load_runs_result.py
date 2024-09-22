from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.schedule_external_sync_log_entry import ScheduleExternalSyncLogEntry


T = TypeVar("T", bound="ScheduleExternalSyncLoadRunsResult")


@_attrs_define
class ScheduleExternalSyncLoadRunsResult:
    """Result.

    Attributes:
        entries (List['ScheduleExternalSyncLogEntry']):
    """

    entries: List["ScheduleExternalSyncLogEntry"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.schedule_external_sync_log_entry import ScheduleExternalSyncLogEntry

        d = src_dict.copy()
        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = ScheduleExternalSyncLogEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        schedule_external_sync_load_runs_result = cls(
            entries=entries,
        )

        schedule_external_sync_load_runs_result.additional_properties = d
        return schedule_external_sync_load_runs_result

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
