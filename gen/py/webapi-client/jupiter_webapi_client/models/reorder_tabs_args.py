from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.home_tab_target import HomeTabTarget

T = TypeVar("T", bound="ReorderTabsArgs")


@_attrs_define
class ReorderTabsArgs:
    """The arguments for reordering tabs in the home config.

    Attributes:
        target (HomeTabTarget): A target for a tab.
        order_of_tabs (list[str]):
    """

    target: HomeTabTarget
    order_of_tabs: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target = self.target.value

        order_of_tabs = self.order_of_tabs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target": target,
                "order_of_tabs": order_of_tabs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        target = HomeTabTarget(d.pop("target"))

        order_of_tabs = cast(list[str], d.pop("order_of_tabs"))

        reorder_tabs_args = cls(
            target=target,
            order_of_tabs=order_of_tabs,
        )

        reorder_tabs_args.additional_properties = d
        return reorder_tabs_args

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
