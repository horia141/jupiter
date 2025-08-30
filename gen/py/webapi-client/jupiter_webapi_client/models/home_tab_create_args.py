from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.home_tab_target import HomeTabTarget
from ..types import UNSET, Unset

T = TypeVar("T", bound="HomeTabCreateArgs")


@_attrs_define
class HomeTabCreateArgs:
    """The arguments for the create home tab use case.

    Attributes:
        target (HomeTabTarget): A target for a tab.
        name (str): The name for an entity which acts as both name and unique identifier.
        icon (Union[None, Unset, str]):
    """

    target: HomeTabTarget
    name: str
    icon: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target = self.target.value

        name = self.name

        icon: Union[None, Unset, str]
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target": target,
                "name": name,
            }
        )
        if icon is not UNSET:
            field_dict["icon"] = icon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        target = HomeTabTarget(d.pop("target"))

        name = d.pop("name")

        def _parse_icon(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        icon = _parse_icon(d.pop("icon", UNSET))

        home_tab_create_args = cls(
            target=target,
            name=name,
            icon=icon,
        )

        home_tab_create_args.additional_properties = d
        return home_tab_create_args

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
