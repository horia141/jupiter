from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.widget_dimension import WidgetDimension

T = TypeVar("T", bound="WidgetGeometry")


@_attrs_define
class WidgetGeometry:
    """A geometry of a widget.

    Attributes:
        row (int):
        col (int):
        dimension (WidgetDimension): A dimension of a widget.
    """

    row: int
    col: int
    dimension: WidgetDimension
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        row = self.row

        col = self.col

        dimension = self.dimension.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "row": row,
                "col": col,
                "dimension": dimension,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        row = d.pop("row")

        col = d.pop("col")

        dimension = WidgetDimension(d.pop("dimension"))

        widget_geometry = cls(
            row=row,
            col=col,
            dimension=dimension,
        )

        widget_geometry.additional_properties = d
        return widget_geometry

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
