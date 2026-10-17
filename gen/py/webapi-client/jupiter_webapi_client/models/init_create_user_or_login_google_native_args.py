from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="InitCreateUserOrLoginGoogleNativeArgs")


@_attrs_define
class InitCreateUserOrLoginGoogleNativeArgs:
    """Init create user or login (native Google sign in) use case arguments.

    Attributes:
        google_auth_code (str): A Google OAuth authorisation code or access token. Never stored.
    """

    google_auth_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        google_auth_code = self.google_auth_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "google_auth_code": google_auth_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        google_auth_code = d.pop("google_auth_code")

        init_create_user_or_login_google_native_args = cls(
            google_auth_code=google_auth_code,
        )

        init_create_user_or_login_google_native_args.additional_properties = d
        return init_create_user_or_login_google_native_args

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
