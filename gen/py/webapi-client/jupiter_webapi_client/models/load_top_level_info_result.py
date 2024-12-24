from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.env import Env
from ..models.hosting import Hosting
from ..models.user_feature import UserFeature
from ..models.workspace_feature import WorkspaceFeature
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.load_top_level_info_result_default_user_feature_flags import (
        LoadTopLevelInfoResultDefaultUserFeatureFlags,
    )
    from ..models.load_top_level_info_result_default_workspace_feature_flags import (
        LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags,
    )
    from ..models.user import User
    from ..models.user_feature_flags_controls import UserFeatureFlagsControls
    from ..models.user_score_overview import UserScoreOverview
    from ..models.workspace import Workspace
    from ..models.workspace_feature_flags_controls import WorkspaceFeatureFlagsControls


T = TypeVar("T", bound="LoadTopLevelInfoResult")


@_attrs_define
class LoadTopLevelInfoResult:
    """Load user and workspace result.

    Attributes:
        env (Env): An environment for a jupiter application.
        hosting (Hosting): The type of hosting jupiter is run into.
        user_feature_flag_controls (UserFeatureFlagsControls): Feature settings controls for the user.
        default_user_feature_flags (LoadTopLevelInfoResultDefaultUserFeatureFlags):
        user_feature_hack (UserFeature): A particular feature of a jupiter user.
        deafult_workspace_name (str): The workspace name.
        default_first_schedule_stream_name (str): The name of a schedule stream.
        default_root_project_name (str): The project name.
        workspace_feature_flag_controls (WorkspaceFeatureFlagsControls): Feature settings controls for the workspace.
        default_workspace_feature_flags (LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags):
        workspace_feature_hack (WorkspaceFeature): A particular feature of a jupiter workspace.
        user (Union['User', None, Unset]):
        user_score_overview (Union['UserScoreOverview', None, Unset]):
        workspace (Union['Workspace', None, Unset]):
    """

    env: Env
    hosting: Hosting
    user_feature_flag_controls: "UserFeatureFlagsControls"
    default_user_feature_flags: "LoadTopLevelInfoResultDefaultUserFeatureFlags"
    user_feature_hack: UserFeature
    deafult_workspace_name: str
    default_first_schedule_stream_name: str
    default_root_project_name: str
    workspace_feature_flag_controls: "WorkspaceFeatureFlagsControls"
    default_workspace_feature_flags: "LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags"
    workspace_feature_hack: WorkspaceFeature
    user: Union["User", None, Unset] = UNSET
    user_score_overview: Union["UserScoreOverview", None, Unset] = UNSET
    workspace: Union["Workspace", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.user import User
        from ..models.user_score_overview import UserScoreOverview
        from ..models.workspace import Workspace

        env = self.env.value

        hosting = self.hosting.value

        user_feature_flag_controls = self.user_feature_flag_controls.to_dict()

        default_user_feature_flags = self.default_user_feature_flags.to_dict()

        user_feature_hack = self.user_feature_hack.value

        deafult_workspace_name = self.deafult_workspace_name

        default_first_schedule_stream_name = self.default_first_schedule_stream_name

        default_root_project_name = self.default_root_project_name

        workspace_feature_flag_controls = self.workspace_feature_flag_controls.to_dict()

        default_workspace_feature_flags = self.default_workspace_feature_flags.to_dict()

        workspace_feature_hack = self.workspace_feature_hack.value

        user: Union[Dict[str, Any], None, Unset]
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, User):
            user = self.user.to_dict()
        else:
            user = self.user

        user_score_overview: Union[Dict[str, Any], None, Unset]
        if isinstance(self.user_score_overview, Unset):
            user_score_overview = UNSET
        elif isinstance(self.user_score_overview, UserScoreOverview):
            user_score_overview = self.user_score_overview.to_dict()
        else:
            user_score_overview = self.user_score_overview

        workspace: Union[Dict[str, Any], None, Unset]
        if isinstance(self.workspace, Unset):
            workspace = UNSET
        elif isinstance(self.workspace, Workspace):
            workspace = self.workspace.to_dict()
        else:
            workspace = self.workspace

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "env": env,
                "hosting": hosting,
                "user_feature_flag_controls": user_feature_flag_controls,
                "default_user_feature_flags": default_user_feature_flags,
                "user_feature_hack": user_feature_hack,
                "deafult_workspace_name": deafult_workspace_name,
                "default_first_schedule_stream_name": default_first_schedule_stream_name,
                "default_root_project_name": default_root_project_name,
                "workspace_feature_flag_controls": workspace_feature_flag_controls,
                "default_workspace_feature_flags": default_workspace_feature_flags,
                "workspace_feature_hack": workspace_feature_hack,
            }
        )
        if user is not UNSET:
            field_dict["user"] = user
        if user_score_overview is not UNSET:
            field_dict["user_score_overview"] = user_score_overview
        if workspace is not UNSET:
            field_dict["workspace"] = workspace

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.load_top_level_info_result_default_user_feature_flags import (
            LoadTopLevelInfoResultDefaultUserFeatureFlags,
        )
        from ..models.load_top_level_info_result_default_workspace_feature_flags import (
            LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags,
        )
        from ..models.user import User
        from ..models.user_feature_flags_controls import UserFeatureFlagsControls
        from ..models.user_score_overview import UserScoreOverview
        from ..models.workspace import Workspace
        from ..models.workspace_feature_flags_controls import WorkspaceFeatureFlagsControls

        d = src_dict.copy()
        env = Env(d.pop("env"))

        hosting = Hosting(d.pop("hosting"))

        user_feature_flag_controls = UserFeatureFlagsControls.from_dict(d.pop("user_feature_flag_controls"))

        default_user_feature_flags = LoadTopLevelInfoResultDefaultUserFeatureFlags.from_dict(
            d.pop("default_user_feature_flags")
        )

        user_feature_hack = UserFeature(d.pop("user_feature_hack"))

        deafult_workspace_name = d.pop("deafult_workspace_name")

        default_first_schedule_stream_name = d.pop("default_first_schedule_stream_name")

        default_root_project_name = d.pop("default_root_project_name")

        workspace_feature_flag_controls = WorkspaceFeatureFlagsControls.from_dict(
            d.pop("workspace_feature_flag_controls")
        )

        default_workspace_feature_flags = LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags.from_dict(
            d.pop("default_workspace_feature_flags")
        )

        workspace_feature_hack = WorkspaceFeature(d.pop("workspace_feature_hack"))

        def _parse_user(data: object) -> Union["User", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_type_0 = User.from_dict(data)

                return user_type_0
            except:  # noqa: E722
                pass
            return cast(Union["User", None, Unset], data)

        user = _parse_user(d.pop("user", UNSET))

        def _parse_user_score_overview(data: object) -> Union["UserScoreOverview", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                user_score_overview_type_0 = UserScoreOverview.from_dict(data)

                return user_score_overview_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserScoreOverview", None, Unset], data)

        user_score_overview = _parse_user_score_overview(d.pop("user_score_overview", UNSET))

        def _parse_workspace(data: object) -> Union["Workspace", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                workspace_type_0 = Workspace.from_dict(data)

                return workspace_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Workspace", None, Unset], data)

        workspace = _parse_workspace(d.pop("workspace", UNSET))

        load_top_level_info_result = cls(
            env=env,
            hosting=hosting,
            user_feature_flag_controls=user_feature_flag_controls,
            default_user_feature_flags=default_user_feature_flags,
            user_feature_hack=user_feature_hack,
            deafult_workspace_name=deafult_workspace_name,
            default_first_schedule_stream_name=default_first_schedule_stream_name,
            default_root_project_name=default_root_project_name,
            workspace_feature_flag_controls=workspace_feature_flag_controls,
            default_workspace_feature_flags=default_workspace_feature_flags,
            workspace_feature_hack=workspace_feature_hack,
            user=user,
            user_score_overview=user_score_overview,
            workspace=workspace,
        )

        load_top_level_info_result.additional_properties = d
        return load_top_level_info_result

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
