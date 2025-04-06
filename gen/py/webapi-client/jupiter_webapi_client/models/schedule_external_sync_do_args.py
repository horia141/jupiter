from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleExternalSyncDoArgs")


@_attrs_define
class ScheduleExternalSyncDoArgs:
    """ScheduleExternalSyncDoArgs.

    Attributes:
        sync_even_if_not_modified (bool):
        today (Union[None, Unset, str]):
        filter_schedule_stream_ref_id (Union[None, Unset, list[str]]):
    """

    sync_even_if_not_modified: bool
    today: Union[None, Unset, str] = UNSET
    filter_schedule_stream_ref_id: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sync_even_if_not_modified = self.sync_even_if_not_modified

        today: Union[None, Unset, str]
        if isinstance(self.today, Unset):
            today = UNSET
        else:
            today = self.today

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
                "sync_even_if_not_modified": sync_even_if_not_modified,
            }
        )
        if today is not UNSET:
            field_dict["today"] = today
        if filter_schedule_stream_ref_id is not UNSET:
            field_dict["filter_schedule_stream_ref_id"] = filter_schedule_stream_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sync_even_if_not_modified = d.pop("sync_even_if_not_modified")

        def _parse_today(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        today = _parse_today(d.pop("today", UNSET))

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

        schedule_external_sync_do_args = cls(
            sync_even_if_not_modified=sync_even_if_not_modified,
            today=today,
            filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
        )

        schedule_external_sync_do_args.additional_properties = d
        return schedule_external_sync_do_args

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
