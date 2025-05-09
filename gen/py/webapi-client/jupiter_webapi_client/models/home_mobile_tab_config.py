from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HomeMobileTabConfig")


@_attrs_define
class HomeMobileTabConfig:
    """A tab on the home page.

    Attributes:
        name (str): The name for an entity which acts as both name and unique identifier.
        widgets (list[list[str]]):
        icon (Union[None, Unset, str]):
    """

    name: str
    widgets: list[list[str]]
    icon: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        widgets = []
        for widgets_item_data in self.widgets:
            widgets_item = widgets_item_data

            widgets.append(widgets_item)

        icon: Union[None, Unset, str]
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "widgets": widgets,
            }
        )
        if icon is not UNSET:
            field_dict["icon"] = icon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        widgets = []
        _widgets = d.pop("widgets")
        for widgets_item_data in _widgets:
            widgets_item = cast(list[str], widgets_item_data)

            widgets.append(widgets_item)

        def _parse_icon(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon = _parse_icon(d.pop("icon", UNSET))

        home_mobile_tab_config = cls(
            name=name,
            widgets=widgets,
            icon=icon,
        )

        home_mobile_tab_config.additional_properties = d
        return home_mobile_tab_config

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
