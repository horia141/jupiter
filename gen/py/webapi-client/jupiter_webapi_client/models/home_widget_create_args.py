from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.widget_dimension import WidgetDimension
from ..models.widget_type import WidgetType

T = TypeVar("T", bound="HomeWidgetCreateArgs")


@_attrs_define
class HomeWidgetCreateArgs:
    """The arguments for the create home widget use case.

    Attributes:
        home_tab_ref_id (str): A generic entity id.
        the_type (WidgetType): A type of widget.
        row (int):
        col (int):
        dimension (WidgetDimension): A dimension of a widget.
    """

    home_tab_ref_id: str
    the_type: WidgetType
    row: int
    col: int
    dimension: WidgetDimension
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        home_tab_ref_id = self.home_tab_ref_id

        the_type = self.the_type.value

        row = self.row

        col = self.col

        dimension = self.dimension.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "home_tab_ref_id": home_tab_ref_id,
                "the_type": the_type,
                "row": row,
                "col": col,
                "dimension": dimension,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        home_tab_ref_id = d.pop("home_tab_ref_id")

        the_type = WidgetType(d.pop("the_type"))

        row = d.pop("row")

        col = d.pop("col")

        dimension = WidgetDimension(d.pop("dimension"))

        home_widget_create_args = cls(
            home_tab_ref_id=home_tab_ref_id,
            the_type=the_type,
            row=row,
            col=col,
            dimension=dimension,
        )

        home_widget_create_args.additional_properties = d
        return home_widget_create_args

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
