"""The command for loading workspaces if they exist."""

from jupiter.core.domain.app import (
    AppCore,
    AppDistribution,
    AppDistributionState,
    AppPlatform,
    AppShell,
)
from jupiter.core.domain.application.gamification.service.score_overview_service import (
    ScoreOverviewService,
)
from jupiter.core.domain.application.gamification.user_score_overview import (
    UserScoreOverview,
)
from jupiter.core.domain.concept.projects.project_name import ProjectName
from jupiter.core.domain.concept.schedule.schedule_stream_name import ScheduleStreamName
from jupiter.core.domain.concept.user.user import User, UserNotFoundError
from jupiter.core.domain.concept.user_workspace_link.user_workspace_link import (
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.concept.workspaces.workspace import (
    Workspace,
    WorkspaceNotFoundError,
)
from jupiter.core.domain.concept.workspaces.workspace_name import WorkspaceName
from jupiter.core.domain.env import Env
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
from jupiter.core.domain.hosting import Hosting
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestReadonlyUseCase,
    AppGuestReadonlyUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class LoadTopLevelInfoArgs(UseCaseArgsBase):
    """Load user and workspsace args."""


@use_case_result
class LoadTopLevelInfoResult(UseCaseResultBase):
    """Load user and workspace result."""

    env: Env
    hosting: Hosting
    user_feature_flag_controls: UserFeatureFlagsControls
    default_user_feature_flags: UserFeatureFlags
    deafult_workspace_name: WorkspaceName
    default_first_schedule_stream_name: ScheduleStreamName
    default_root_project_name: ProjectName
    workspace_feature_flag_controls: WorkspaceFeatureFlagsControls
    default_workspace_feature_flags: WorkspaceFeatureFlags
    workspace_feature_hack: WorkspaceFeature
    user: User | None
    user_score_overview: UserScoreOverview | None
    workspace: Workspace | None
    user_feature_hack: UserFeature | None
    app_core_hack: AppCore | None
    app_shell_hack: AppShell | None
    app_platform_hack: AppPlatform | None
    app_distribution_hack: AppDistribution | None
    app_distribution_state_hack: AppDistributionState | None


class LoadTopLevelInfoUseCase(
    AppGuestReadonlyUseCase[LoadTopLevelInfoArgs, LoadTopLevelInfoResult],
):
    """The command for loading a user and workspace if they exist and other data too."""

    async def _execute(
        self,
        context: AppGuestReadonlyUseCaseContext,
        args: LoadTopLevelInfoArgs,
    ) -> LoadTopLevelInfoResult:
        """Execute the command's action."""
        (
            user_feature_flags_controls,
            workspace_feature_flags_controls,
        ) = infer_feature_flag_controls(self._global_properties)

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            if context.auth_token is None:
                user = None
                workspace = None
                user_score_overview = None
            else:
                try:
                    user = await uow.get_for(User).load_by_id(
                        context.auth_token.user_ref_id
                    )
                    user_workspace_link = await uow.get(
                        UserWorkspaceLinkRepository
                    ).load_by_user(context.auth_token.user_ref_id)
                    workspace = await uow.get_for(Workspace).load_by_id(
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
            deafult_workspace_name=WorkspaceName("Work"),
            default_first_schedule_stream_name=ScheduleStreamName("Events"),
            default_root_project_name=ProjectName("Life"),
            workspace_feature_flag_controls=workspace_feature_flags_controls,
            default_workspace_feature_flags=BASIC_WORKSPACE_FEATURE_FLAGS,
            workspace_feature_hack=WorkspaceFeature.INBOX_TASKS,
            user=user,
            user_score_overview=user_score_overview,
            workspace=workspace,
            user_feature_hack=UserFeature.GAMIFICATION,
            app_core_hack=AppCore.WEBUI,
            app_shell_hack=AppShell.BROWSER,
            app_platform_hack=AppPlatform.DESKTOP_MACOS,
            app_distribution_hack=AppDistribution.WEB,
            app_distribution_state_hack=AppDistributionState.READY,
        )
