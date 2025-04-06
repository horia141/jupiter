from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.user import User
    from ..models.workspace import Workspace


T = TypeVar("T", bound="InitResult")


@_attrs_define
class InitResult:
    """Init use case result.

    Attributes:
        new_user (User): A user of jupiter.
        new_workspace (Workspace): The workspace where everything happens.
        auth_token_ext (str): An externally facing authentication token.
        recovery_token (str): A recovery token for auth systems.
    """

    new_user: "User"
    new_workspace: "Workspace"
    auth_token_ext: str
    recovery_token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        new_user = self.new_user.to_dict()

        new_workspace = self.new_workspace.to_dict()

        auth_token_ext = self.auth_token_ext

        recovery_token = self.recovery_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "new_user": new_user,
                "new_workspace": new_workspace,
                "auth_token_ext": auth_token_ext,
                "recovery_token": recovery_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User
        from ..models.workspace import Workspace

        d = dict(src_dict)
        new_user = User.from_dict(d.pop("new_user"))

        new_workspace = Workspace.from_dict(d.pop("new_workspace"))

        auth_token_ext = d.pop("auth_token_ext")

        recovery_token = d.pop("recovery_token")

        init_result = cls(
            new_user=new_user,
            new_workspace=new_workspace,
            auth_token_ext=auth_token_ext,
            recovery_token=recovery_token,
        )

        init_result.additional_properties = d
        return init_result

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
