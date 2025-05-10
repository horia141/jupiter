from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.widget_geometry import WidgetGeometry


T = TypeVar("T", bound="HomeTabWidgetPlacementSection")


@_attrs_define
class HomeTabWidgetPlacementSection:
    """A section of the placement of widgets on a tab.

    Attributes:
        ref_id (str): A generic entity id.
        geometry (WidgetGeometry): A geometry of a widget.
    """

    ref_id: str
    geometry: "WidgetGeometry"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref_id = self.ref_id

        geometry = self.geometry.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref_id": ref_id,
                "geometry": geometry,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_geometry import WidgetGeometry

        d = dict(src_dict)
        ref_id = d.pop("ref_id")

        geometry = WidgetGeometry.from_dict(d.pop("geometry"))

        home_tab_widget_placement_section = cls(
            ref_id=ref_id,
            geometry=geometry,
        )

        home_tab_widget_placement_section.additional_properties = d
        return home_tab_widget_placement_section

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
