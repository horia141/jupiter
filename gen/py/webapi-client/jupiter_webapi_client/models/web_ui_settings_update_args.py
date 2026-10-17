from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.web_ui_settings_update_args_use_night_mode import WebUiSettingsUpdateArgsUseNightMode


T = TypeVar("T", bound="WebUiSettingsUpdateArgs")


@_attrs_define
class WebUiSettingsUpdateArgs:
    """Web UI settings update args.

    Attributes:
        use_night_mode (WebUiSettingsUpdateArgsUseNightMode):
    """

    use_night_mode: WebUiSettingsUpdateArgsUseNightMode
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        use_night_mode = self.use_night_mode.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "use_night_mode": use_night_mode,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.web_ui_settings_update_args_use_night_mode import WebUiSettingsUpdateArgsUseNightMode  # noqa: PLC0415

        d = dict(src_dict)
        use_night_mode = WebUiSettingsUpdateArgsUseNightMode.from_dict(d.pop("use_night_mode"))

        web_ui_settings_update_args = cls(
            use_night_mode=use_night_mode,
        )

        web_ui_settings_update_args.additional_properties = d
        return web_ui_settings_update_args

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
