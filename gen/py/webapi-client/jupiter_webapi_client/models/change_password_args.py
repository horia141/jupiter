from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ChangePasswordArgs")


@_attrs_define
class ChangePasswordArgs:
    """Change password args.

    Attributes:
        current_password (str): A new password in plain text, as received from a user.
        new_password (str): A new password in plain text, as received from a user.
        new_password_repeat (str): A new password in plain text, as received from a user.
    """

    current_password: str
    new_password: str
    new_password_repeat: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        current_password = self.current_password

        new_password = self.new_password

        new_password_repeat = self.new_password_repeat

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_password": current_password,
                "new_password": new_password,
                "new_password_repeat": new_password_repeat,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        current_password = d.pop("current_password")

        new_password = d.pop("new_password")

        new_password_repeat = d.pop("new_password_repeat")

        change_password_args = cls(
            current_password=current_password,
            new_password=new_password,
            new_password_repeat=new_password_repeat,
        )

        change_password_args.additional_properties = d
        return change_password_args

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
