from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_summary import EntitySummary
    from ..models.schedule_external_sync_log_per_stream_result import ScheduleExternalSyncLogPerStreamResult


T = TypeVar("T", bound="ScheduleExternalSyncLogEntry")


@_attrs_define
class ScheduleExternalSyncLogEntry:
    """An entry in a sync log.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        schedule_external_sync_log_ref_id (str):
        source (EventSource): The source of the modification which this event records.
        today (str): A date or possibly a datetime for the application.
        start_of_window (str): A date or possibly a datetime for the application.
        end_of_window (str): A date or possibly a datetime for the application.
        sync_even_if_not_modified (bool):
        opened (bool):
        per_stream_results (list['ScheduleExternalSyncLogPerStreamResult']):
        entity_records (list['EntitySummary']):
        even_more_entity_records (bool):
        archived_time (Union[None, Unset, str]):
        filter_schedule_stream_ref_id (Union[None, Unset, list[str]]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    schedule_external_sync_log_ref_id: str
    source: EventSource
    today: str
    start_of_window: str
    end_of_window: str
    sync_even_if_not_modified: bool
    opened: bool
    per_stream_results: list["ScheduleExternalSyncLogPerStreamResult"]
    entity_records: list["EntitySummary"]
    even_more_entity_records: bool
    archived_time: Union[None, Unset, str] = UNSET
    filter_schedule_stream_ref_id: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        schedule_external_sync_log_ref_id = self.schedule_external_sync_log_ref_id

        source = self.source.value

        today = self.today

        start_of_window = self.start_of_window

        end_of_window = self.end_of_window

        sync_even_if_not_modified = self.sync_even_if_not_modified

        opened = self.opened

        per_stream_results = []
        for per_stream_results_item_data in self.per_stream_results:
            per_stream_results_item = per_stream_results_item_data.to_dict()
            per_stream_results.append(per_stream_results_item)

        entity_records = []
        for entity_records_item_data in self.entity_records:
            entity_records_item = entity_records_item_data.to_dict()
            entity_records.append(entity_records_item)

        even_more_entity_records = self.even_more_entity_records

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        filter_schedule_stream_ref_id: Union[None, Unset, list[str]]
        if isinstance(self.filter_schedule_stream_ref_id, Unset):
            filter_schedule_stream_ref_id = UNSET
        elif isinstance(self.filter_schedule_stream_ref_id, list):
            filter_schedule_stream_ref_id = self.filter_schedule_stream_ref_id

        else:
            filter_schedule_stream_ref_id = self.filter_schedule_stream_ref_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "schedule_external_sync_log_ref_id": schedule_external_sync_log_ref_id,
                "source": source,
                "today": today,
                "start_of_window": start_of_window,
                "end_of_window": end_of_window,
                "sync_even_if_not_modified": sync_even_if_not_modified,
                "opened": opened,
                "per_stream_results": per_stream_results,
                "entity_records": entity_records,
                "even_more_entity_records": even_more_entity_records,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if filter_schedule_stream_ref_id is not UNSET:
            field_dict["filter_schedule_stream_ref_id"] = filter_schedule_stream_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary
        from ..models.schedule_external_sync_log_per_stream_result import ScheduleExternalSyncLogPerStreamResult

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        schedule_external_sync_log_ref_id = d.pop("schedule_external_sync_log_ref_id")

        source = EventSource(d.pop("source"))

        today = d.pop("today")

        start_of_window = d.pop("start_of_window")

        end_of_window = d.pop("end_of_window")

        sync_even_if_not_modified = d.pop("sync_even_if_not_modified")

        opened = d.pop("opened")

        per_stream_results = []
        _per_stream_results = d.pop("per_stream_results")
        for per_stream_results_item_data in _per_stream_results:
            per_stream_results_item = ScheduleExternalSyncLogPerStreamResult.from_dict(per_stream_results_item_data)

            per_stream_results.append(per_stream_results_item)

        entity_records = []
        _entity_records = d.pop("entity_records")
        for entity_records_item_data in _entity_records:
            entity_records_item = EntitySummary.from_dict(entity_records_item_data)

            entity_records.append(entity_records_item)

        even_more_entity_records = d.pop("even_more_entity_records")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_filter_schedule_stream_ref_id(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_schedule_stream_ref_id_type_0 = cast(list[str], data)

                return filter_schedule_stream_ref_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_schedule_stream_ref_id = _parse_filter_schedule_stream_ref_id(
            d.pop("filter_schedule_stream_ref_id", UNSET)
        )

        schedule_external_sync_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            schedule_external_sync_log_ref_id=schedule_external_sync_log_ref_id,
            source=source,
            today=today,
            start_of_window=start_of_window,
            end_of_window=end_of_window,
            sync_even_if_not_modified=sync_even_if_not_modified,
            opened=opened,
            per_stream_results=per_stream_results,
            entity_records=entity_records,
            even_more_entity_records=even_more_entity_records,
            archived_time=archived_time,
            filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
        )

        schedule_external_sync_log_entry.additional_properties = d
        return schedule_external_sync_log_entry

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
