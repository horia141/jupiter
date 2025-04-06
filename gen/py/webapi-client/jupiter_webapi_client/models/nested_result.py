from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.nested_result_per_source import NestedResultPerSource


T = TypeVar("T", bound="NestedResult")


@_attrs_define
class NestedResult:
    """A result broken down by the various sources of inbox tasks.

    Attributes:
        total_cnt (int):
        per_source_cnt (list['NestedResultPerSource']):
    """

    total_cnt: int
    per_source_cnt: list["NestedResultPerSource"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_cnt = self.total_cnt

        per_source_cnt = []
        for per_source_cnt_item_data in self.per_source_cnt:
            per_source_cnt_item = per_source_cnt_item_data.to_dict()
            per_source_cnt.append(per_source_cnt_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_cnt": total_cnt,
                "per_source_cnt": per_source_cnt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.nested_result_per_source import NestedResultPerSource

        d = dict(src_dict)
        total_cnt = d.pop("total_cnt")

        per_source_cnt = []
        _per_source_cnt = d.pop("per_source_cnt")
        for per_source_cnt_item_data in _per_source_cnt:
            per_source_cnt_item = NestedResultPerSource.from_dict(per_source_cnt_item_data)

            per_source_cnt.append(per_source_cnt_item)

        nested_result = cls(
            total_cnt=total_cnt,
            per_source_cnt=per_source_cnt,
        )

        nested_result.additional_properties = d
        return nested_result

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
