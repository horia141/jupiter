from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResetPasswordArgs")


@_attrs_define
class ResetPasswordArgs:
    """Reset password args.

    Attributes:
        email_address (str): An email address.
        recovery_token (str): A recovery token for auth systems.
        new_password (str): A new password in plain text, as received from a user.
        new_password_repeat (str): A new password in plain text, as received from a user.
    """

    email_address: str
    recovery_token: str
    new_password: str
    new_password_repeat: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email_address = self.email_address

        recovery_token = self.recovery_token

        new_password = self.new_password

        new_password_repeat = self.new_password_repeat

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_address": email_address,
                "recovery_token": recovery_token,
                "new_password": new_password,
                "new_password_repeat": new_password_repeat,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email_address = d.pop("email_address")

        recovery_token = d.pop("recovery_token")

        new_password = d.pop("new_password")

        new_password_repeat = d.pop("new_password_repeat")

        reset_password_args = cls(
            email_address=email_address,
            recovery_token=recovery_token,
            new_password=new_password,
            new_password_repeat=new_password_repeat,
        )

        reset_password_args.additional_properties = d
        return reset_password_args

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
