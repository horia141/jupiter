from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_widget import HomeWidget


T = TypeVar("T", bound="HomeWidgetLoadResult")


@_attrs_define
class HomeWidgetLoadResult:
    """The result of loading a home widget.

    Attributes:
        widget (HomeWidget): A widget on the home page.
    """

    widget: "HomeWidget"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        widget = self.widget.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "widget": widget,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_widget import HomeWidget

        d = dict(src_dict)
        widget = HomeWidget.from_dict(d.pop("widget"))

        home_widget_load_result = cls(
            widget=widget,
        )

        home_widget_load_result.additional_properties = d
        return home_widget_load_result

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
