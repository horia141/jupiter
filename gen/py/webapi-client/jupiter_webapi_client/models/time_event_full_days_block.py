from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.time_event_namespace import TimeEventNamespace
from ..types import UNSET, Unset

T = TypeVar("T", bound="TimeEventFullDaysBlock")


@_attrs_define
class TimeEventFullDaysBlock:
    """A full day block of time.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name for an entity which acts as both name and unique identifier.
        time_event_domain_ref_id (str):
        namespace (TimeEventNamespace): Time event namespaces.
        source_entity_ref_id (str): A generic entity id.
        start_date (str): A date or possibly a datetime for the application.
        duration_days (int):
        end_date (str): A date or possibly a datetime for the application.
        archived_time (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    time_event_domain_ref_id: str
    namespace: TimeEventNamespace
    source_entity_ref_id: str
    start_date: str
    duration_days: int
    end_date: str
    archived_time: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        time_event_domain_ref_id = self.time_event_domain_ref_id

        namespace = self.namespace.value

        source_entity_ref_id = self.source_entity_ref_id

        start_date = self.start_date

        duration_days = self.duration_days

        end_date = self.end_date

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

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
                "time_event_domain_ref_id": time_event_domain_ref_id,
                "namespace": namespace,
                "source_entity_ref_id": source_entity_ref_id,
                "start_date": start_date,
                "duration_days": duration_days,
                "end_date": end_date,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        version = d.pop("version")

        archived = d.pop("archived")

        created_time = d.pop("created_time")

        last_modified_time = d.pop("last_modified_time")

        name = d.pop("name")

        time_event_domain_ref_id = d.pop("time_event_domain_ref_id")

        namespace = TimeEventNamespace(d.pop("namespace"))

        source_entity_ref_id = d.pop("source_entity_ref_id")

        start_date = d.pop("start_date")

        duration_days = d.pop("duration_days")

        end_date = d.pop("end_date")

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        time_event_full_days_block = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            time_event_domain_ref_id=time_event_domain_ref_id,
            namespace=namespace,
            source_entity_ref_id=source_entity_ref_id,
            start_date=start_date,
            duration_days=duration_days,
            end_date=end_date,
            archived_time=archived_time,
        )

        time_event_full_days_block.additional_properties = d
        return time_event_full_days_block

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
