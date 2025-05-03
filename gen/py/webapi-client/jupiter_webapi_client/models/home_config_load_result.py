from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_config import HomeConfig


T = TypeVar("T", bound="HomeConfigLoadResult")


@_attrs_define
class HomeConfigLoadResult:
    """The result of the home config load use case.

    Attributes:
        home_config (HomeConfig): The home config entity.
    """

    home_config: "HomeConfig"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        home_config = self.home_config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "home_config": home_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_config import HomeConfig

        d = dict(src_dict)
        home_config = HomeConfig.from_dict(d.pop("home_config"))

        home_config_load_result = cls(
            home_config=home_config,
        )

        home_config_load_result.additional_properties = d
        return home_config_load_result

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
