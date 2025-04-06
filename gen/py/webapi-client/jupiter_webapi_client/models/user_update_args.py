from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user_update_args_name import UserUpdateArgsName
    from ..models.user_update_args_timezone import UserUpdateArgsTimezone


T = TypeVar("T", bound="UserUpdateArgs")


@_attrs_define
class UserUpdateArgs:
    """User update args.

    Attributes:
        name (UserUpdateArgsName):
        timezone (UserUpdateArgsTimezone):
    """

    name: "UserUpdateArgsName"
    timezone: "UserUpdateArgsTimezone"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name.to_dict()

        timezone = self.timezone.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "timezone": timezone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_update_args_name import UserUpdateArgsName
        from ..models.user_update_args_timezone import UserUpdateArgsTimezone

        d = dict(src_dict)
        name = UserUpdateArgsName.from_dict(d.pop("name"))

        timezone = UserUpdateArgsTimezone.from_dict(d.pop("timezone"))

        user_update_args = cls(
            name=name,
            timezone=timezone,
        )

        user_update_args.additional_properties = d
        return user_update_args

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
