from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metric_entry_update_args_collection_time import MetricEntryUpdateArgsCollectionTime
    from ..models.metric_entry_update_args_value import MetricEntryUpdateArgsValue


T = TypeVar("T", bound="MetricEntryUpdateArgs")


@_attrs_define
class MetricEntryUpdateArgs:
    """PersonFindArgs.

    Attributes:
        ref_id (str): A generic entity id.
        collection_time (MetricEntryUpdateArgsCollectionTime):
        value (MetricEntryUpdateArgsValue):
    """

    ref_id: str
    collection_time: "MetricEntryUpdateArgsCollectionTime"
    value: "MetricEntryUpdateArgsValue"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ref_id = self.ref_id

        collection_time = self.collection_time.to_dict()

        value = self.value.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "collection_time": collection_time,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metric_entry_update_args_collection_time import MetricEntryUpdateArgsCollectionTime
        from ..models.metric_entry_update_args_value import MetricEntryUpdateArgsValue

        d = src_dict.copy()
        ref_id = d.pop("ref_id")

        collection_time = MetricEntryUpdateArgsCollectionTime.from_dict(d.pop("collection_time"))

        value = MetricEntryUpdateArgsValue.from_dict(d.pop("value"))

        metric_entry_update_args = cls(
            ref_id=ref_id,
            collection_time=collection_time,
            value=value,
        )

        metric_entry_update_args.additional_properties = d
        return metric_entry_update_args

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
