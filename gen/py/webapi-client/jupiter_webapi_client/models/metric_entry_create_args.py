from typing import Any, Dict, List, Type, TypeVar, Union

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
        collection_time (Union[Unset, str]): A date or possibly a datetime for the application.
    """

    metric_ref_id: str
    value: float
    collection_time: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        metric_ref_id = self.metric_ref_id

        value = self.value

        collection_time = self.collection_time

        field_dict: Dict[str, Any] = {}
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
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        metric_ref_id = d.pop("metric_ref_id")

        value = d.pop("value")

        collection_time = d.pop("collection_time", UNSET)

        metric_entry_create_args = cls(
            metric_ref_id=metric_ref_id,
            value=value,
            collection_time=collection_time,
        )

        metric_entry_create_args.additional_properties = d
        return metric_entry_create_args

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
