from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MetricChangeCollectionProjectArgs")


@_attrs_define
class MetricChangeCollectionProjectArgs:
    """PersonFindArgs.

    Attributes:
        collection_project_ref_id (str): A generic entity id.
    """

    collection_project_ref_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        collection_project_ref_id = self.collection_project_ref_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collection_project_ref_id": collection_project_ref_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        collection_project_ref_id = d.pop("collection_project_ref_id")

        metric_change_collection_project_args = cls(
            collection_project_ref_id=collection_project_ref_id,
        )

        metric_change_collection_project_args.additional_properties = d
        return metric_change_collection_project_args

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
