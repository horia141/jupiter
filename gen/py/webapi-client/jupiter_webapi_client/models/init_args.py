from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_feature import UserFeature
from ..models.workspace_feature import WorkspaceFeature

T = TypeVar("T", bound="InitArgs")


@_attrs_define
class InitArgs:
    """Init use case arguments.

    Attributes:
        for_app_review (bool):
        user_email_address (str): An email address.
        user_name (str): The user name for a user of jupiter.
        user_timezone (str): A timezone in this domain.
        user_feature_flags (List[UserFeature]):
        auth_password (str): A new password in plain text, as received from a user.
        auth_password_repeat (str): A new password in plain text, as received from a user.
        workspace_name (str): The workspace name.
        workspace_first_schedule_stream_name (str): The name of a schedule stream.
        workspace_root_project_name (str): The project name.
        workspace_feature_flags (List[WorkspaceFeature]):
    """

    for_app_review: bool
    user_email_address: str
    user_name: str
    user_timezone: str
    user_feature_flags: List[UserFeature]
    auth_password: str
    auth_password_repeat: str
    workspace_name: str
    workspace_first_schedule_stream_name: str
    workspace_root_project_name: str
    workspace_feature_flags: List[WorkspaceFeature]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        for_app_review = self.for_app_review

        user_email_address = self.user_email_address

        user_name = self.user_name

        user_timezone = self.user_timezone

        user_feature_flags = []
        for user_feature_flags_item_data in self.user_feature_flags:
            user_feature_flags_item = user_feature_flags_item_data.value
            user_feature_flags.append(user_feature_flags_item)

        auth_password = self.auth_password

        auth_password_repeat = self.auth_password_repeat

        workspace_name = self.workspace_name

        workspace_first_schedule_stream_name = self.workspace_first_schedule_stream_name

        workspace_root_project_name = self.workspace_root_project_name

        workspace_feature_flags = []
        for workspace_feature_flags_item_data in self.workspace_feature_flags:
            workspace_feature_flags_item = workspace_feature_flags_item_data.value
            workspace_feature_flags.append(workspace_feature_flags_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "for_app_review": for_app_review,
                "user_email_address": user_email_address,
                "user_name": user_name,
                "user_timezone": user_timezone,
                "user_feature_flags": user_feature_flags,
                "auth_password": auth_password,
                "auth_password_repeat": auth_password_repeat,
                "workspace_name": workspace_name,
                "workspace_first_schedule_stream_name": workspace_first_schedule_stream_name,
                "workspace_root_project_name": workspace_root_project_name,
                "workspace_feature_flags": workspace_feature_flags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        for_app_review = d.pop("for_app_review")

        user_email_address = d.pop("user_email_address")

        user_name = d.pop("user_name")

        user_timezone = d.pop("user_timezone")

        user_feature_flags = []
        _user_feature_flags = d.pop("user_feature_flags")
        for user_feature_flags_item_data in _user_feature_flags:
            user_feature_flags_item = UserFeature(user_feature_flags_item_data)

            user_feature_flags.append(user_feature_flags_item)

        auth_password = d.pop("auth_password")

        auth_password_repeat = d.pop("auth_password_repeat")

        workspace_name = d.pop("workspace_name")

        workspace_first_schedule_stream_name = d.pop("workspace_first_schedule_stream_name")

        workspace_root_project_name = d.pop("workspace_root_project_name")

        workspace_feature_flags = []
        _workspace_feature_flags = d.pop("workspace_feature_flags")
        for workspace_feature_flags_item_data in _workspace_feature_flags:
            workspace_feature_flags_item = WorkspaceFeature(workspace_feature_flags_item_data)

            workspace_feature_flags.append(workspace_feature_flags_item)

        init_args = cls(
            for_app_review=for_app_review,
            user_email_address=user_email_address,
            user_name=user_name,
            user_timezone=user_timezone,
            user_feature_flags=user_feature_flags,
            auth_password=auth_password,
            auth_password_repeat=auth_password_repeat,
            workspace_name=workspace_name,
            workspace_first_schedule_stream_name=workspace_first_schedule_stream_name,
            workspace_root_project_name=workspace_root_project_name,
            workspace_feature_flags=workspace_feature_flags,
        )

        init_args.additional_properties = d
        return init_args

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
