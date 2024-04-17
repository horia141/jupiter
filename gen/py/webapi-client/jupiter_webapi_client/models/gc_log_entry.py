from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..models.sync_target import SyncTarget
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entity_summary import EntitySummary


T = TypeVar("T", bound="GCLogEntry")


@_attrs_define
class GCLogEntry:
    """A particular entry in the GC log.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        gc_log_ref_id (str):
        source (EventSource): The source of the modification which this event records.
        gc_targets (List[SyncTarget]):
        opened (bool):
        entity_records (List['EntitySummary']):
        archived_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    gc_log_ref_id: str
    source: EventSource
    gc_targets: List[SyncTarget]
    opened: bool
    entity_records: List["EntitySummary"]
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        gc_log_ref_id = self.gc_log_ref_id

        source = self.source.value

        gc_targets = []
        for gc_targets_item_data in self.gc_targets:
            gc_targets_item = gc_targets_item_data.value
            gc_targets.append(gc_targets_item)

        opened = self.opened

        entity_records = []
        for entity_records_item_data in self.entity_records:
            entity_records_item = entity_records_item_data.to_dict()
            entity_records.append(entity_records_item)

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "version": version,
                "archived": archived,
                "created_time": created_time,
                "last_modified_time": last_modified_time,
                "name": name,
                "gc_log_ref_id": gc_log_ref_id,
                "source": source,
                "gc_targets": gc_targets,
                "opened": opened,
                "entity_records": entity_records,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.entity_summary import EntitySummary

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        gc_log_ref_id = d.pop("gc_log_ref_id")

        source = EventSource(d.pop("source"))

        gc_targets = []
        _gc_targets = d.pop("gc_targets")
        for gc_targets_item_data in _gc_targets:
            gc_targets_item = SyncTarget(gc_targets_item_data)

            gc_targets.append(gc_targets_item)

        opened = d.pop("opened")

        entity_records = []
        _entity_records = d.pop("entity_records")
        for entity_records_item_data in _entity_records:
            entity_records_item = EntitySummary.from_dict(entity_records_item_data)

            entity_records.append(entity_records_item)

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        gc_log_entry = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            gc_log_ref_id=gc_log_ref_id,
            source=source,
            gc_targets=gc_targets,
            opened=opened,
            entity_records=entity_records,
            archived_time=archived_time,
        )

        gc_log_entry.additional_properties = d
        return gc_log_entry

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
