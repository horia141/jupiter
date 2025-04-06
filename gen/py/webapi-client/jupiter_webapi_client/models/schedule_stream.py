from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.schedule_source import ScheduleSource
from ..models.schedule_stream_color import ScheduleStreamColor
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleStream")


@_attrs_define
class ScheduleStream:
    """A schedule group or stream of events.

    Attributes:
        ref_id (str): A generic entity id.
        version (int):
        archived (bool):
        created_time (str): A timestamp in the application.
        last_modified_time (str): A timestamp in the application.
        name (str): The name of a schedule stream.
        schedule_domain_ref_id (str):
        source (ScheduleSource): The source of a schedule.
        color (ScheduleStreamColor): The color of a particular schedule stream.
        archived_time (Union[None, Unset, str]):
        source_ical_url (Union[None, Unset, str]):
    """

    ref_id: str
    version: int
    archived: bool
    created_time: str
    last_modified_time: str
    name: str
    schedule_domain_ref_id: str
    source: ScheduleSource
    color: ScheduleStreamColor
    archived_time: Union[None, Unset, str] = UNSET
    source_ical_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        version = self.version

        archived = self.archived

        created_time = self.created_time

        last_modified_time = self.last_modified_time

        name = self.name

        schedule_domain_ref_id = self.schedule_domain_ref_id

        source = self.source.value

        color = self.color.value

        archived_time: Union[None, Unset, str]
        if isinstance(self.archived_time, Unset):
            archived_time = UNSET
        else:
            archived_time = self.archived_time

        source_ical_url: Union[None, Unset, str]
        if isinstance(self.source_ical_url, Unset):
            source_ical_url = UNSET
        else:
            source_ical_url = self.source_ical_url

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
                "source": source,
                "color": color,
            }
        )
        if archived_time is not UNSET:
            field_dict["archived_time"] = archived_time
        if source_ical_url is not UNSET:
            field_dict["source_ical_url"] = source_ical_url

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

        source = ScheduleSource(d.pop("source"))

        color = ScheduleStreamColor(d.pop("color"))

        def _parse_archived_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        archived_time = _parse_archived_time(d.pop("archived_time", UNSET))

        def _parse_source_ical_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        source_ical_url = _parse_source_ical_url(d.pop("source_ical_url", UNSET))

        schedule_stream = cls(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            name=name,
            schedule_domain_ref_id=schedule_domain_ref_id,
            source=source,
            color=color,
            archived_time=archived_time,
            source_ical_url=source_ical_url,
        )

        schedule_stream.additional_properties = d
        return schedule_stream

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
