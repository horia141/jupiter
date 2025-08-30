from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_summary import EntitySummary


T = TypeVar("T", bound="StatsLogEntry")


@_attrs_define
class StatsLogEntry:
    """A particular entry in the stats log.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        stats_log_ref_id (str):
        source (EventSource): The source of the modification which this event records.
        stats_targets (list[SyncTarget]):
        today (str): A date or possibly a datetime for the application.
        opened (bool):
        entity_records (list['EntitySummary']):
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        filter_big_plan_ref_ids (Union[None, Unset, list[str]]):
        filter_journal_ref_ids (Union[None, Unset, list[str]]):
        filter_habit_ref_ids (Union[None, Unset, list[str]]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    stats_log_ref_id: str
    source: EventSource
    stats_targets: list[SyncTarget]
    today: str
    opened: bool
    entity_records: list["EntitySummary"]
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    filter_big_plan_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_journal_ref_ids: Union[None, Unset, list[str]] = UNSET
    filter_habit_ref_ids: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        stats_log_ref_id = self.stats_log_ref_id

        source = self.source.value

        stats_targets = []
        for stats_targets_item_data in self.stats_targets:
            stats_targets_item = stats_targets_item_data.value
            stats_targets.append(stats_targets_item)

        today = self.today

        opened = self.opened

        entity_records = []
        for entity_records_item_data in self.entity_records:
            entity_records_item = entity_records_item_data.to_dict()
            entity_records.append(entity_records_item)

        archival_reason: Union[None, Unset, str]
        if isinstance(self.archival_reason, Unset):
            archival_reason = UNSET
        else:
            archival_reason = self.archival_reason

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        filter_big_plan_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_big_plan_ref_ids, Unset):
            filter_big_plan_ref_ids = UNSET
        elif isinstance(self.filter_big_plan_ref_ids, list):
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        else:
            filter_big_plan_ref_ids = self.filter_big_plan_ref_ids

        filter_journal_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_journal_ref_ids, Unset):
            filter_journal_ref_ids = UNSET
        elif isinstance(self.filter_journal_ref_ids, list):
            filter_journal_ref_ids = self.filter_journal_ref_ids

        else:
            filter_journal_ref_ids = self.filter_journal_ref_ids

        filter_habit_ref_ids: Union[None, Unset, list[str]]
        if isinstance(self.filter_habit_ref_ids, Unset):
            filter_habit_ref_ids = UNSET
        elif isinstance(self.filter_habit_ref_ids, list):
            filter_habit_ref_ids = self.filter_habit_ref_ids

        else:
            filter_habit_ref_ids = self.filter_habit_ref_ids

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
                "stats_log_ref_id": stats_log_ref_id,
                "source": source,
                "stats_targets": stats_targets,
                "today": today,
                "opened": opened,
                "entity_records": entity_records,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if filter_big_plan_ref_ids is not UNSET:
            field_dict["filter_big_plan_ref_ids"] = filter_big_plan_ref_ids
        if filter_journal_ref_ids is not UNSET:
            field_dict["filter_journal_ref_ids"] = filter_journal_ref_ids
        if filter_habit_ref_ids is not UNSET:
            field_dict["filter_habit_ref_ids"] = filter_habit_ref_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        stats_log_ref_id = d.pop("stats_log_ref_id")

        source = EventSource(d.pop("source"))

        stats_targets = []
        _stats_targets = d.pop("stats_targets")
        for stats_targets_item_data in _stats_targets:
            stats_targets_item = SyncTarget(stats_targets_item_data)

            stats_targets.append(stats_targets_item)

        today = d.pop("today")

        opened = d.pop("opened")

        entity_records = []
        _entity_records = d.pop("entity_records")
        for entity_records_item_data in _entity_records:
            entity_records_item = EntitySummary.from_dict(entity_records_item_data)

            entity_records.append(entity_records_item)

        def _parse_archival_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archival_reason = _parse_archival_reason(d.pop("archival_reason", UNSET))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_filter_big_plan_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_big_plan_ref_ids_type_0 = cast(list[str], data)

                return filter_big_plan_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_big_plan_ref_ids = _parse_filter_big_plan_ref_ids(d.pop("filter_big_plan_ref_ids", UNSET))

        def _parse_filter_journal_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_journal_ref_ids_type_0 = cast(list[str], data)

                return filter_journal_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_journal_ref_ids = _parse_filter_journal_ref_ids(d.pop("filter_journal_ref_ids", UNSET))

        def _parse_filter_habit_ref_ids(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_habit_ref_ids_type_0 = cast(list[str], data)

                return filter_habit_ref_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        filter_habit_ref_ids = _parse_filter_habit_ref_ids(d.pop("filter_habit_ref_ids", UNSET))

        stats_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            stats_log_ref_id=stats_log_ref_id,
            source=source,
            stats_targets=stats_targets,
            today=today,
            opened=opened,
            entity_records=entity_records,
            archival_reason=archival_reason,
            archived_time=archived_time,
            filter_big_plan_ref_ids=filter_big_plan_ref_ids,
            filter_journal_ref_ids=filter_journal_ref_ids,
            filter_habit_ref_ids=filter_habit_ref_ids,
        )

        stats_log_entry.additional_properties = d
        return stats_log_entry

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
