from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

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
        env (Env): An environment for a Jupiter application.
        hosting (Hosting): The type of hosting Jupiter is run into.
        user_feature_flag_controls (UserFeatureFlagsControls): Feature settings controls for the user.
        default_user_feature_flags (LoadTopLevelInfoResultDefaultUserFeatureFlags):
        user_feature_hack (UserFeature): A particular feature of a Jupiter user.
        deafult_workspace_name (str): The workspace name.
        default_root_project_name (str): The project name.
        workspace_feature_flag_controls (WorkspaceFeatureFlagsControls): Feature settings controls for the workspace.
        default_workspace_feature_flags (LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags):
        workspace_feature_hack (WorkspaceFeature): A particular feature of a Jupiter workspace.
        user (Union[Unset, User]): A user of Jupiter.
        user_score_overview (Union[Unset, UserScoreOverview]): An overview of the scores for a user.
        workspace (Union[Unset, Workspace]): The workspace where everything happens.
    """

    env: Env
    hosting: Hosting
    user_feature_flag_controls: "UserFeatureFlagsControls"
    default_user_feature_flags: "LoadTopLevelInfoResultDefaultUserFeatureFlags"
    user_feature_hack: UserFeature
    deafult_workspace_name: str
    default_root_project_name: str
    workspace_feature_flag_controls: "WorkspaceFeatureFlagsControls"
    default_workspace_feature_flags: "LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags"
    workspace_feature_hack: WorkspaceFeature
    user: Union[Unset, "User"] = UNSET
    user_score_overview: Union[Unset, "UserScoreOverview"] = UNSET
    workspace: Union[Unset, "Workspace"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        env = self.env.value

        hosting = self.hosting.value

        user_feature_flag_controls = self.user_feature_flag_controls.to_dict()

        default_user_feature_flags = self.default_user_feature_flags.to_dict()

        user_feature_hack = self.user_feature_hack.value

        deafult_workspace_name = self.deafult_workspace_name

        default_root_project_name = self.default_root_project_name

        workspace_feature_flag_controls = self.workspace_feature_flag_controls.to_dict()

        default_workspace_feature_flags = self.default_workspace_feature_flags.to_dict()

        workspace_feature_hack = self.workspace_feature_hack.value

        user: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        user_score_overview: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.user_score_overview, Unset):
            user_score_overview = self.user_score_overview.to_dict()

        workspace: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.workspace, Unset):
            workspace = self.workspace.to_dict()

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

        default_root_project_name = d.pop("default_root_project_name")

        workspace_feature_flag_controls = WorkspaceFeatureFlagsControls.from_dict(
            d.pop("workspace_feature_flag_controls")
        )

        default_workspace_feature_flags = LoadTopLevelInfoResultDefaultWorkspaceFeatureFlags.from_dict(
            d.pop("default_workspace_feature_flags")
        )

        workspace_feature_hack = WorkspaceFeature(d.pop("workspace_feature_hack"))

        _user = d.pop("user", UNSET)
        user: Union[Unset, User]
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = User.from_dict(_user)

        _user_score_overview = d.pop("user_score_overview", UNSET)
        user_score_overview: Union[Unset, UserScoreOverview]
        if isinstance(_user_score_overview, Unset):
            user_score_overview = UNSET
        else:
            user_score_overview = UserScoreOverview.from_dict(_user_score_overview)

        _workspace = d.pop("workspace", UNSET)
        workspace: Union[Unset, Workspace]
        if isinstance(_workspace, Unset):
            workspace = UNSET
        else:
            workspace = Workspace.from_dict(_workspace)

        load_top_level_info_result = cls(
            env=env,
            hosting=hosting,
            user_feature_flag_controls=user_feature_flag_controls,
            default_user_feature_flags=default_user_feature_flags,
            user_feature_hack=user_feature_hack,
            deafult_workspace_name=deafult_workspace_name,
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
