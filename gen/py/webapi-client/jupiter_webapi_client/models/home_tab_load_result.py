from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_tab import HomeTab
    from ..models.home_widget import HomeWidget


T = TypeVar("T", bound="HomeTabLoadResult")


@_attrs_define
class HomeTabLoadResult:
    """The result of loading a home tab.

    Attributes:
        tab (HomeTab): A tab on the home page.
        widgets (list['HomeWidget']):
    """

    tab: "HomeTab"
    widgets: list["HomeWidget"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tab = self.tab.to_dict()

        widgets = []
        for widgets_item_data in self.widgets:
            widgets_item = widgets_item_data.to_dict()
            widgets.append(widgets_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tab": tab,
                "widgets": widgets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_tab import HomeTab
        from ..models.home_widget import HomeWidget

        d = dict(src_dict)
        tab = HomeTab.from_dict(d.pop("tab"))

        widgets = []
        _widgets = d.pop("widgets")
        for widgets_item_data in _widgets:
            widgets_item = HomeWidget.from_dict(widgets_item_data)

            widgets.append(widgets_item)

        home_tab_load_result = cls(
            tab=tab,
            widgets=widgets,
        )

        home_tab_load_result.additional_properties = d
        return home_tab_load_result

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
