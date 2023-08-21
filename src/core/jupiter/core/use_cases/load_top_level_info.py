"""The command for loading workspaces if they exist."""
from dataclasses import dataclass
from typing import Final, Optional

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import (
    BASIC_USER_FEATURE_FLAGS,
    BASIC_WORKSPACE_FEATURE_FLAGS,
    UserFeature,
    UserFeatureFlags,
    UserFeatureFlagsControls,
    WorkspaceFeature,
    WorkspaceFeatureFlags,
    WorkspaceFeatureFlagsControls,
)
from jupiter.core.domain.gamification.service.score_overview_service import (
    ScoreOverviewService,
)
from jupiter.core.domain.gamification.user_score_overview import UserScoreOverview
from jupiter.core.domain.hosting import Hosting
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.user.infra.user_repository import UserNotFoundError
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.env import Env
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestReadonlyUseCase,
    AppGuestUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class LoadTopLevelInfoArgs(UseCaseArgsBase):
    """Load user and workspsace args."""


@dataclass
class LoadTopLevelInfoResult(UseCaseResultBase):
    """Load user and workspace result."""

    env: Env
    hosting: Hosting
    user_feature_flag_controls: UserFeatureFlagsControls
    default_user_feature_flags: UserFeatureFlags
    user_feature_hack: UserFeature
    deafult_workspace_name: WorkspaceName
    default_first_project_name: ProjectName
    workspace_feature_flag_controls: WorkspaceFeatureFlagsControls
    default_workspace_feature_flags: WorkspaceFeatureFlags
    workspace_feature_hack: WorkspaceFeature
    user: Optional[User] = None
    user_score_overview: UserScoreOverview | None = None
    workspace: Optional[Workspace] = None


class LoadTopLevelInfoUseCase(
    AppGuestReadonlyUseCase[LoadTopLevelInfoArgs, LoadTopLevelInfoResult],
):
    """The command for loading a user and workspace if they exist and other data too."""

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]

    def __init__(
        self,
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
        global_properties: GlobalProperties,
        time_provider: TimeProvider,
    ) -> None:
        """Constructor."""
        super().__init__(auth_token_stamper, storage_engine)
        self._global_properties = global_properties
        self._time_provider = time_provider

    async def _execute(
        self,
        context: AppGuestUseCaseContext,
        args: LoadTopLevelInfoArgs,
    ) -> LoadTopLevelInfoResult:
        """Execute the command's action."""
        (
            user_feature_flags_controls,
            workspace_feature_flags_controls,
        ) = infer_feature_flag_controls(self._global_properties)

        async with self._storage_engine.get_unit_of_work() as uow:
            if context.auth_token is None:
                user = None
                workspace = None
                user_score_overview = None
            else:
                try:
                    user = await uow.user_repository.load_by_id(
                        context.auth_token.user_ref_id
                    )
                    user_workspace_link = (
                        await uow.user_workspace_link_repository.load_by_user(
                            context.auth_token.user_ref_id
                        )
                    )
                    workspace = await uow.workspace_repository.load_by_id(
                        user_workspace_link.workspace_ref_id
                    )
                    if user.is_feature_available(UserFeature.GAMIFICATION):
                        user_score_overview = await ScoreOverviewService().do_it(
                            uow, user, self._time_provider.get_current_time()
                        )
                    else:
                        user_score_overview = None
                except (UserNotFoundError, WorkspaceNotFoundError):
                    user = None
                    workspace = None
                    user_score_overview = None

        return LoadTopLevelInfoResult(
            env=self._global_properties.env,
            hosting=self._global_properties.hosting,
            user_feature_flag_controls=user_feature_flags_controls,
            default_user_feature_flags=BASIC_USER_FEATURE_FLAGS,
            user_feature_hack=UserFeature.GAMIFICATION,
            deafult_workspace_name=WorkspaceName.from_raw("Work"),
            default_first_project_name=ProjectName.from_raw("Work"),
            workspace_feature_flag_controls=workspace_feature_flags_controls,
            default_workspace_feature_flags=BASIC_WORKSPACE_FEATURE_FLAGS,
            workspace_feature_hack=WorkspaceFeature.INBOX_TASKS,
            user=user,
            user_score_overview=user_score_overview,
            workspace=workspace,
        )
