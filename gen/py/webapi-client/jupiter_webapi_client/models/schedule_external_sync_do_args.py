from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_source import EventSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduleExternalSyncDoArgs")


@_attrs_define
class ScheduleExternalSyncDoArgs:
    """ScheduleExternalSyncDoArgs.

    Attributes:
        source (EventSource): The source of the modification which this event records.
        filter_schedule_stream_ref_id (Union[List[str], None, Unset]):
    """

    source: EventSource
    filter_schedule_stream_ref_id: Union[List[str], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source = self.source.value

        filter_schedule_stream_ref_id: Union[List[str], None, Unset]
        if isinstance(self.filter_schedule_stream_ref_id, Unset):
            filter_schedule_stream_ref_id = UNSET
        elif isinstance(self.filter_schedule_stream_ref_id, list):
            filter_schedule_stream_ref_id = self.filter_schedule_stream_ref_id

        else:
            filter_schedule_stream_ref_id = self.filter_schedule_stream_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
            }
        )
        if filter_schedule_stream_ref_id is not UNSET:
            field_dict["filter_schedule_stream_ref_id"] = filter_schedule_stream_ref_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source = EventSource(d.pop("source"))

        def _parse_filter_schedule_stream_ref_id(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                filter_schedule_stream_ref_id_type_0 = cast(List[str], data)

                return filter_schedule_stream_ref_id_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        filter_schedule_stream_ref_id = _parse_filter_schedule_stream_ref_id(
            d.pop("filter_schedule_stream_ref_id", UNSET)
        )

        schedule_external_sync_do_args = cls(
            source=source,
            filter_schedule_stream_ref_id=filter_schedule_stream_ref_id,
        )

        schedule_external_sync_do_args.additional_properties = d
        return schedule_external_sync_do_args

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
