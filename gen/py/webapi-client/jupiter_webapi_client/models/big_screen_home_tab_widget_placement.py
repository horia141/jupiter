from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.big_screen_home_tab_widget_placement_kind import BigScreenHomeTabWidgetPlacementKind

if TYPE_CHECKING:
    from ..models.home_tab_widget_placement_section import HomeTabWidgetPlacementSection


T = TypeVar("T", bound="BigScreenHomeTabWidgetPlacement")


@_attrs_define
class BigScreenHomeTabWidgetPlacement:
    """The placement of widgets on a tab for big screen.

    Attributes:
        kind (BigScreenHomeTabWidgetPlacementKind):
        matrix (list[list[Union[None, str]]]):
        sections (list['HomeTabWidgetPlacementSection']):
    """

    kind: BigScreenHomeTabWidgetPlacementKind
    matrix: list[list[Union[None, str]]]
    sections: list["HomeTabWidgetPlacementSection"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind.value

        matrix = []
        for matrix_item_data in self.matrix:
            matrix_item = []
            for matrix_item_item_data in matrix_item_data:
                matrix_item_item: Union[None, str]
                matrix_item_item = matrix_item_item_data
                matrix_item.append(matrix_item_item)

            matrix.append(matrix_item)

        sections = []
        for sections_item_data in self.sections:
            sections_item = sections_item_data.to_dict()
            sections.append(sections_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "matrix": matrix,
                "sections": sections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_tab_widget_placement_section import HomeTabWidgetPlacementSection

        d = dict(src_dict)
        kind = BigScreenHomeTabWidgetPlacementKind(d.pop("kind"))

        matrix = []
        _matrix = d.pop("matrix")
        for matrix_item_data in _matrix:
            matrix_item = []
            _matrix_item = matrix_item_data
            for matrix_item_item_data in _matrix_item:

                def _parse_matrix_item_item(data: object) -> Union[None, str]:
                    if data is None:
                        return data
                    return cast(Union[None, str], data)

                matrix_item_item = _parse_matrix_item_item(matrix_item_item_data)

                matrix_item.append(matrix_item_item)

            matrix.append(matrix_item)

        sections = []
        _sections = d.pop("sections")
        for sections_item_data in _sections:
            sections_item = HomeTabWidgetPlacementSection.from_dict(sections_item_data)

            sections.append(sections_item)

        big_screen_home_tab_widget_placement = cls(
            kind=kind,
            matrix=matrix,
            sections=sections,
        )

        big_screen_home_tab_widget_placement.additional_properties = d
        return big_screen_home_tab_widget_placement

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
