from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InitCreateUserOrLoginAppleNativeArgs")


@_attrs_define
class InitCreateUserOrLoginAppleNativeArgs:
    """Init create user or login (native Apple sign in) use case arguments.

    Attributes:
        apple_auth_code (str): An Apple OAuth authorisation code or access token. Never stored.
        apple_user_json (None | str | Unset):
    """

    apple_auth_code: str
    apple_user_json: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        apple_auth_code = self.apple_auth_code

        apple_user_json: None | str | Unset
        if isinstance(self.apple_user_json, Unset):
            apple_user_json = UNSET
        else:
            apple_user_json = self.apple_user_json

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apple_auth_code": apple_auth_code,
            }
        )
        if apple_user_json is not UNSET:
            field_dict["apple_user_json"] = apple_user_json

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        apple_auth_code = d.pop("apple_auth_code")

        def _parse_apple_user_json(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        apple_user_json = _parse_apple_user_json(d.pop("apple_user_json", UNSET))

        init_create_user_or_login_apple_native_args = cls(
            apple_auth_code=apple_auth_code,
            apple_user_json=apple_user_json,
        )

        init_create_user_or_login_apple_native_args.additional_properties = d
        return init_create_user_or_login_apple_native_args

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
