"""UseCase for initialising a workspace."""
from argparse import Namespace
from typing import Final, cast

from jupiter.cli.command.command import GuestMutationCommand
from jupiter.cli.session_storage import SessionInfo, SessionStorage
from jupiter.cli.top_level_context import TopLevelContext
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.features import (
    UserFeature,
    UserFeatureFlags,
    WorkspaceFeature,
    WorkspaceFeatureFlags,
)
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.secure import secure_class
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from jupiter.core.use_cases.init import InitArgs, InitUseCase
from rich.console import Console
from rich.text import Text


@secure_class
class Initialize(GuestMutationCommand[InitUseCase]):
    """UseCase class for initialising a workspace."""

    _top_level_context: Final[TopLevelContext]

    def __init__(
        self,
        session_storage: SessionStorage,
        top_level_context: TopLevelContext,
        use_case: InitUseCase,
    ) -> None:
        """Constructor."""
        super().__init__(session_storage, use_case)
        self._top_level_context = top_level_context

    async def _run(
        self,
        session_info: SessionInfo | None,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        user_email_address = EmailAddress.from_raw(args.user_email_address)
        user_name = UserName.from_raw(args.user_name)
        user_timezone = Timezone.from_raw(args.user_timezone)
        user_feature_flags: UserFeatureFlags = {}
        for enabled_feature in args.user_feature_flag_enabled:
            user_feature_flags[UserFeature(enabled_feature)] = True
        for disabled_feature in args.user_feature_flag_disable:
            user_feature_flags[UserFeature(disabled_feature)] = False
        auth_password = cast(PasswordNewPlain, args.auth_password)
        auth_password_repeat = cast(PasswordNewPlain, args.auth_password_repeat)
        workspace_name = WorkspaceName.from_raw(args.workspace_name)
        workspace_first_project_name = ProjectName.from_raw(
            args.workspace_first_project_name
        )
        workspace_feature_flags: WorkspaceFeatureFlags = {}
        for enabled_feature in args.workspace_feature_flag_enabled:
            workspace_feature_flags[WorkspaceFeature(enabled_feature)] = True
        for disabled_feature in args.workspace_feature_flag_disable:
            workspace_feature_flags[WorkspaceFeature(disabled_feature)] = False

        result = await self._use_case.execute(
            AppGuestUseCaseSession(
                session_info.auth_token_ext if session_info else None
            ),
            InitArgs(
                user_email_address=user_email_address,
                user_name=user_name,
                user_timezone=user_timezone,
                user_feature_flags=user_feature_flags,
                auth_password=auth_password,
                auth_password_repeat=auth_password_repeat,
                workspace_name=workspace_name,
                workspace_first_project_name=workspace_first_project_name,
                workspace_feature_flags=workspace_feature_flags,
            ),
        )

        self._session_storage.store(SessionInfo(auth_token_ext=result.auth_token_ext))

        rich_text = Text("Your recovery token is ")
        rich_text.append(result.recovery_token.token, style="bold green")
        rich_text.append("\nStore it in a safe place!", style="bold red")

        console = Console()
        console.print(rich_text)

    @property
    def should_have_streaming_progress_report(self) -> bool:
        """Whether the main script should have a streaming progress reporter."""
        return False
