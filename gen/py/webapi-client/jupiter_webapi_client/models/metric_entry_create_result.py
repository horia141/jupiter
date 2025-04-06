from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metric_entry import MetricEntry


T = TypeVar("T", bound="MetricEntryCreateResult")


@_attrs_define
class MetricEntryCreateResult:
    """MetricEntryCreate result.

    Attributes:
        new_metric_entry (MetricEntry): A metric entry.
    """

    new_metric_entry: "MetricEntry"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_metric_entry = self.new_metric_entry.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_metric_entry": new_metric_entry,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metric_entry import MetricEntry

        d = dict(src_dict)
        new_metric_entry = MetricEntry.from_dict(d.pop("new_metric_entry"))

        metric_entry_create_result = cls(
            new_metric_entry=new_metric_entry,
        )

        metric_entry_create_result.additional_properties = d
        return metric_entry_create_result

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
