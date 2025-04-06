from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricEntryCreateArgs")


@_attrs_define
class MetricEntryCreateArgs:
    """MetricEntryCreate args.

    Attributes:
        metric_ref_id (str): A generic entity id.
        value (float):
        collection_time (Union[None, Unset, str]):
    """

    metric_ref_id: str
    value: float
    collection_time: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metric_ref_id = self.metric_ref_id

        value = self.value

        collection_time: Union[None, Unset, str]
        if isinstance(self.collection_time, Unset):
            collection_time = UNSET
        else:
            collection_time = self.collection_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric_ref_id": metric_ref_id,
                "value": value,
            }
        )
        if collection_time is not UNSET:
            field_dict["collection_time"] = collection_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        metric_ref_id = d.pop("metric_ref_id")

        value = d.pop("value")

        def _parse_collection_time(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        collection_time = _parse_collection_time(d.pop("collection_time", UNSET))

        metric_entry_create_args = cls(
            metric_ref_id=metric_ref_id,
            value=value,
            collection_time=collection_time,
        )

        metric_entry_create_args.additional_properties = d
        return metric_entry_create_args

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
