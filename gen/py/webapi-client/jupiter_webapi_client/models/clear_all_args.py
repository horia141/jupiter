from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_feature import UserFeature
from ..models.workspace_feature import WorkspaceFeature
from ..types import UNSET, Unset

T = TypeVar("T", bound="ClearAllArgs")


@_attrs_define
class ClearAllArgs:
    """PersonFindArgs.

    Attributes:
        user_name (str): The user name for a user of Jupiter.
        user_timezone (str): A timezone in this domain.
        auth_current_password (str): A new password in plain text, as received from a user.
        auth_new_password (str): A new password in plain text, as received from a user.
        auth_new_password_repeat (str): A new password in plain text, as received from a user.
        workspace_name (str): The workspace name.
        workspace_root_project_name (str): The project name.
        user_feature_flags (Union[List[UserFeature], None, Unset]):
        workspace_feature_flags (Union[List[WorkspaceFeature], None, Unset]):
    """

    user_name: str
    user_timezone: str
    auth_current_password: str
    auth_new_password: str
    auth_new_password_repeat: str
    workspace_name: str
    workspace_root_project_name: str
    user_feature_flags: Union[List[UserFeature], None, Unset] = UNSET
    workspace_feature_flags: Union[List[WorkspaceFeature], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_name = self.user_name

        user_timezone = self.user_timezone

        auth_current_password = self.auth_current_password

        auth_new_password = self.auth_new_password

        auth_new_password_repeat = self.auth_new_password_repeat

        workspace_name = self.workspace_name

        workspace_root_project_name = self.workspace_root_project_name

        user_feature_flags: Union[List[str], None, Unset]
        if isinstance(self.user_feature_flags, Unset):
            user_feature_flags = UNSET
        elif isinstance(self.user_feature_flags, list):
            user_feature_flags = []
            for user_feature_flags_type_0_item_data in self.user_feature_flags:
                user_feature_flags_type_0_item = user_feature_flags_type_0_item_data.value
                user_feature_flags.append(user_feature_flags_type_0_item)

        else:
            user_feature_flags = self.user_feature_flags

        workspace_feature_flags: Union[List[str], None, Unset]
        if isinstance(self.workspace_feature_flags, Unset):
            workspace_feature_flags = UNSET
        elif isinstance(self.workspace_feature_flags, list):
            workspace_feature_flags = []
            for workspace_feature_flags_type_0_item_data in self.workspace_feature_flags:
                workspace_feature_flags_type_0_item = workspace_feature_flags_type_0_item_data.value
                workspace_feature_flags.append(workspace_feature_flags_type_0_item)

        else:
            workspace_feature_flags = self.workspace_feature_flags

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_name": user_name,
                "user_timezone": user_timezone,
                "auth_current_password": auth_current_password,
                "auth_new_password": auth_new_password,
                "auth_new_password_repeat": auth_new_password_repeat,
                "workspace_name": workspace_name,
                "workspace_root_project_name": workspace_root_project_name,
            }
        )
        if user_feature_flags is not UNSET:
            field_dict["user_feature_flags"] = user_feature_flags
        if workspace_feature_flags is not UNSET:
            field_dict["workspace_feature_flags"] = workspace_feature_flags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        user_name = d.pop("user_name")

        user_timezone = d.pop("user_timezone")

        auth_current_password = d.pop("auth_current_password")

        auth_new_password = d.pop("auth_new_password")

        auth_new_password_repeat = d.pop("auth_new_password_repeat")

        workspace_name = d.pop("workspace_name")

        workspace_root_project_name = d.pop("workspace_root_project_name")

        def _parse_user_feature_flags(data: object) -> Union[List[UserFeature], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                user_feature_flags_type_0 = []
                _user_feature_flags_type_0 = data
                for user_feature_flags_type_0_item_data in _user_feature_flags_type_0:
                    user_feature_flags_type_0_item = UserFeature(user_feature_flags_type_0_item_data)

                    user_feature_flags_type_0.append(user_feature_flags_type_0_item)

                return user_feature_flags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[UserFeature], None, Unset], data)

        user_feature_flags = _parse_user_feature_flags(d.pop("user_feature_flags", UNSET))

        def _parse_workspace_feature_flags(data: object) -> Union[List[WorkspaceFeature], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                workspace_feature_flags_type_0 = []
                _workspace_feature_flags_type_0 = data
                for workspace_feature_flags_type_0_item_data in _workspace_feature_flags_type_0:
                    workspace_feature_flags_type_0_item = WorkspaceFeature(workspace_feature_flags_type_0_item_data)

                    workspace_feature_flags_type_0.append(workspace_feature_flags_type_0_item)

                return workspace_feature_flags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[WorkspaceFeature], None, Unset], data)

        workspace_feature_flags = _parse_workspace_feature_flags(d.pop("workspace_feature_flags", UNSET))

        clear_all_args = cls(
            user_name=user_name,
            user_timezone=user_timezone,
            auth_current_password=auth_current_password,
            auth_new_password=auth_new_password,
            auth_new_password_repeat=auth_new_password_repeat,
            workspace_name=workspace_name,
            workspace_root_project_name=workspace_root_project_name,
            user_feature_flags=user_feature_flags,
            workspace_feature_flags=workspace_feature_flags,
        )

        clear_all_args.additional_properties = d
        return clear_all_args

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
