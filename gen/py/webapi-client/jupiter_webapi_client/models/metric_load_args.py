from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MetricLoadArgs")


@_attrs_define
class MetricLoadArgs:
    """MetricLoadArgs.

    Attributes:
        ref_id (str): A generic entity id.
        allow_archived (bool):
        allow_archived_entries (bool):
        collection_task_retrieve_offset (Union[None, Unset, int]):
    """

    ref_id: str
    allow_archived: bool
    allow_archived_entries: bool
    collection_task_retrieve_offset: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        allow_archived = self.allow_archived

        allow_archived_entries = self.allow_archived_entries

        collection_task_retrieve_offset: Union[None, Unset, int]
        if isinstance(self.collection_task_retrieve_offset, Unset):
            collection_task_retrieve_offset = UNSET
        else:
            collection_task_retrieve_offset = self.collection_task_retrieve_offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "allow_archived": allow_archived,
                "allow_archived_entries": allow_archived_entries,
            }
        )
        if collection_task_retrieve_offset is not UNSET:
            field_dict["collection_task_retrieve_offset"] = collection_task_retrieve_offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        allow_archived = d.pop("allow_archived")

        allow_archived_entries = d.pop("allow_archived_entries")

        def _parse_collection_task_retrieve_offset(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        collection_task_retrieve_offset = _parse_collection_task_retrieve_offset(
            d.pop("collection_task_retrieve_offset", UNSET)
        )

        metric_load_args = cls(
            ref_id=ref_id,
            allow_archived=allow_archived,
            allow_archived_entries=allow_archived_entries,
            collection_task_retrieve_offset=collection_task_retrieve_offset,
        )

        metric_load_args.additional_properties = d
        return metric_load_args

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
