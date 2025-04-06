from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleExternalSyncLogPerStreamResult")


@_attrs_define
class ScheduleExternalSyncLogPerStreamResult:
    """The result of syncing a stream.

    Attributes:
        schedule_stream_ref_id (str): A generic entity id.
        success (bool):
        error_msg (Union[None, Unset, str]):
    """

    schedule_stream_ref_id: str
    success: bool
    error_msg: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schedule_stream_ref_id = self.schedule_stream_ref_id

        success = self.success

        error_msg: Union[None, Unset, str]
        if isinstance(self.error_msg, Unset):
            error_msg = UNSET
        else:
            error_msg = self.error_msg

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "schedule_stream_ref_id": schedule_stream_ref_id,
                "success": success,
            }
        )
        if error_msg is not UNSET:
            field_dict["error_msg"] = error_msg

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        schedule_stream_ref_id = d.pop("schedule_stream_ref_id")

        success = d.pop("success")

        def _parse_error_msg(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_msg = _parse_error_msg(d.pop("error_msg", UNSET))

        schedule_external_sync_log_per_stream_result = cls(
            schedule_stream_ref_id=schedule_stream_ref_id,
            success=success,
            error_msg=error_msg,
        )

        schedule_external_sync_log_per_stream_result.additional_properties = d
        return schedule_external_sync_log_per_stream_result

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
