from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.home_tab import HomeTab


T = TypeVar("T", bound="HomeTabCreateResult")


@_attrs_define
class HomeTabCreateResult:
    """The result of the create home tab use case.

    Attributes:
        new_home_tab (HomeTab): A tab on the home page.
    """

    new_home_tab: "HomeTab"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_home_tab = self.new_home_tab.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_home_tab": new_home_tab,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_tab import HomeTab

        d = dict(src_dict)
        new_home_tab = HomeTab.from_dict(d.pop("new_home_tab"))

        home_tab_create_result = cls(
            new_home_tab=new_home_tab,
        )

        home_tab_create_result.additional_properties = d
        return home_tab_create_result

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
