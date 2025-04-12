from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schedule_source import ScheduleSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleEventInDay")


@_attrs_define
class ScheduleEventInDay:
    """An event in a schedule.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name of a schedule event.
        schedule_domain_ref_id (str):
        schedule_stream_ref_id (str): A generic entity id.
        source (ScheduleSource): The source of a schedule.
        archival_reason (Union[None, Unset, str]):
        archived_time (Union[None, Unset, str]):
        external_uid (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    schedule_domain_ref_id: str
    schedule_stream_ref_id: str
    source: ScheduleSource
    archival_reason: Union[None, Unset, str] = UNSET
    archived_time: Union[None, Unset, str] = UNSET
    external_uid: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        schedule_domain_ref_id = self.schedule_domain_ref_id

        schedule_stream_ref_id = self.schedule_stream_ref_id

        source = self.source.value

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

        external_uid: Union[None, Unset, str]
        if isinstance(self.external_uid, Unset):
            external_uid = UNSET
        else:
            external_uid = self.external_uid

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
                "schedule_domain_ref_id": schedule_domain_ref_id,
                "schedule_stream_ref_id": schedule_stream_ref_id,
                "source": source,
            }
        )
        if archival_reason is not UNSET:
            field_dict["archival_reason"] = archival_reason
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if external_uid is not UNSET:
            field_dict["external_uid"] = external_uid

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

        schedule_domain_ref_id = d.pop("schedule_domain_ref_id")

        schedule_stream_ref_id = d.pop("schedule_stream_ref_id")

        source = ScheduleSource(d.pop("source"))

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

        def _parse_external_uid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_uid = _parse_external_uid(d.pop("external_uid", UNSET))

        schedule_event_in_day = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            schedule_domain_ref_id=schedule_domain_ref_id,
            schedule_stream_ref_id=schedule_stream_ref_id,
            source=source,
            archival_reason=archival_reason,
            archived_time=archived_time,
            external_uid=external_uid,
        )

        schedule_event_in_day.additional_properties = d
        return schedule_event_in_day

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
