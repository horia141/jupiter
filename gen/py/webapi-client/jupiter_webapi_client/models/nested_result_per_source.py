from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.inbox_task_source import InboxTaskSource

T = TypeVar("T", bound="NestedResultPerSource")


@_attrs_define
class NestedResultPerSource:
    """A particular result broken down by the various sources of inbox tasks.

    Attributes:
        source (InboxTaskSource): The origin of an inbox task.
        count (int):
    """

    source: InboxTaskSource
    count: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        source = self.source.value

        count = self.count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "count": count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        source = InboxTaskSource(d.pop("source"))

        count = d.pop("count")

        nested_result_per_source = cls(
            source=source,
            count=count,
        )

        nested_result_per_source.additional_properties = d
        return nested_result_per_source

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
