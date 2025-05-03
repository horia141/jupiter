from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_config_update_args_key_habits import HomeConfigUpdateArgsKeyHabits
    from ..models.home_config_update_args_key_metrics import HomeConfigUpdateArgsKeyMetrics


T = TypeVar("T", bound="HomeConfigUpdateArgs")


@_attrs_define
class HomeConfigUpdateArgs:
    """The arguments for updating the home config.

    Attributes:
        key_habits (HomeConfigUpdateArgsKeyHabits):
        key_metrics (HomeConfigUpdateArgsKeyMetrics):
    """

    key_habits: "HomeConfigUpdateArgsKeyHabits"
    key_metrics: "HomeConfigUpdateArgsKeyMetrics"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key_habits = self.key_habits.to_dict()

        key_metrics = self.key_metrics.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key_habits": key_habits,
                "key_metrics": key_metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_config_update_args_key_habits import HomeConfigUpdateArgsKeyHabits
        from ..models.home_config_update_args_key_metrics import HomeConfigUpdateArgsKeyMetrics

        d = dict(src_dict)
        key_habits = HomeConfigUpdateArgsKeyHabits.from_dict(d.pop("key_habits"))

        key_metrics = HomeConfigUpdateArgsKeyMetrics.from_dict(d.pop("key_metrics"))

        home_config_update_args = cls(
            key_habits=key_habits,
            key_metrics=key_metrics,
        )

        home_config_update_args.additional_properties = d
        return home_config_update_args

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
