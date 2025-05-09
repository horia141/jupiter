from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_mobile_tab_config import HomeMobileTabConfig


T = TypeVar("T", bound="HomeMobileConfig")


@_attrs_define
class HomeMobileConfig:
    """A mobile config for the home page.

    Attributes:
        home_config_ref_id (str):
        tabs (list['HomeMobileTabConfig']):
    """

    home_config_ref_id: str
    tabs: list["HomeMobileTabConfig"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        home_config_ref_id = self.home_config_ref_id

        tabs = []
        for tabs_item_data in self.tabs:
            tabs_item = tabs_item_data.to_dict()
            tabs.append(tabs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "home_config_ref_id": home_config_ref_id,
                "tabs": tabs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_mobile_tab_config import HomeMobileTabConfig

        d = dict(src_dict)
        home_config_ref_id = d.pop("home_config_ref_id")

        tabs = []
        _tabs = d.pop("tabs")
        for tabs_item_data in _tabs:
            tabs_item = HomeMobileTabConfig.from_dict(tabs_item_data)

            tabs.append(tabs_item)

        home_mobile_config = cls(
            home_config_ref_id=home_config_ref_id,
            tabs=tabs,
        )

        home_mobile_config.additional_properties = d
        return home_mobile_config

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
