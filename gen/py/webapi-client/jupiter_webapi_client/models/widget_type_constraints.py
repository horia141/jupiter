from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.widget_dimension import WidgetDimension

T = TypeVar("T", bound="WidgetTypeConstraints")


@_attrs_define
class WidgetTypeConstraints:
    """A constraints for a widget type.

    Attributes:
        allowed_dimensions (list[WidgetDimension]):
        for_desktop (bool):
        for_mobile (bool):
    """

    allowed_dimensions: list[WidgetDimension]
    for_desktop: bool
    for_mobile: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_dimensions = []
        for allowed_dimensions_item_data in self.allowed_dimensions:
            allowed_dimensions_item = allowed_dimensions_item_data.value
            allowed_dimensions.append(allowed_dimensions_item)

        for_desktop = self.for_desktop

        for_mobile = self.for_mobile

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "allowed_dimensions": allowed_dimensions,
                "for_desktop": for_desktop,
                "for_mobile": for_mobile,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allowed_dimensions = []
        _allowed_dimensions = d.pop("allowed_dimensions")
        for allowed_dimensions_item_data in _allowed_dimensions:
            allowed_dimensions_item = WidgetDimension(allowed_dimensions_item_data)

            allowed_dimensions.append(allowed_dimensions_item)

        for_desktop = d.pop("for_desktop")

        for_mobile = d.pop("for_mobile")

        widget_type_constraints = cls(
            allowed_dimensions=allowed_dimensions,
            for_desktop=for_desktop,
            for_mobile=for_mobile,
        )

        widget_type_constraints.additional_properties = d
        return widget_type_constraints

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
