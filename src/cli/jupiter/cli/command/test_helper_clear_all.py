"""Test helper command for clearing all branch and leaf entities."""
from argparse import ArgumentParser, Namespace
from typing import Final, cast

from jupiter.cli.command.command import TestHelperCommand
from jupiter.cli.session_storage import SessionStorage
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.features import (
    UserFeature,
    UserFeatureFlags,
    WorkspaceFeature,
    WorkspaceFeatureFlags,
)
from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.test_helper.clear_all import ClearAllArgs, ClearAllUseCase


class TestHelperClearAll(TestHelperCommand):
    """Test helper command for clearing all branch and leaf entities."""

    _session_storage: Final[SessionStorage]
    _use_case: Final[ClearAllUseCase]

    def __init__(
        self, session_storage: SessionStorage, use_case: ClearAllUseCase
    ) -> None:
        """Constructor."""
        self._session_storage = session_storage
        self._use_case = use_case

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "test-helper-clear-all"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Clear all the data in the workspace"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--user-name",
            required=True,
            dest="user_name",
            help="The user name to use",
        )
        parser.add_argument(
            "--user-timezone",
            required=True,
            dest="user_timezone",
            help="The user timezone to use",
        )
        parser.add_argument(
            "--user-feature",
            dest="user_feature_flag_enabled",
            default=[],
            action="append",
            choices=UserFeature.all_values(),
        )
        parser.add_argument(
            "--user-no-feature",
            dest="user_feature_flag_disable",
            default=[],
            action="append",
            choices=UserFeature.all_values(),
        )
        parser.add_argument(
            "--auth-current-password",
            type=PasswordPlain.from_raw,
            dest="auth_current_password",
            required=True,
            help="The current password for the user",
        )
        parser.add_argument(
            "--auth-new-password",
            type=PasswordNewPlain.from_raw,
            dest="auth_new_password",
            required=True,
            help="The new password",
        )
        parser.add_argument(
            "--auth-new-password-repeat",
            type=PasswordNewPlain.from_raw,
            dest="auth_new_password_repeat",
            required=True,
            help="A repeat of the new password",
        )
        parser.add_argument(
            "--workspace-name",
            required=True,
            dest="workspace_name",
            help="The workspace name to use",
        )
        parser.add_argument(
            "--workspace-default-project",
            dest="workspace_default_project_ref_id",
            required=False,
            help="The project key to use as a general default",
        )
        parser.add_argument(
            "--workspace-feature",
            dest="workspace_feature_flag_enabled",
            default=[],
            action="append",
            choices=WorkspaceFeature.all_values(),
        )
        parser.add_argument(
            "--workspace-no-feature",
            dest="workspace_feature_flag_disable",
            default=[],
            action="append",
            choices=WorkspaceFeature.all_values(),
        )

    async def run(
        self,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        user_name = UserName.from_raw(args.user_name)
        user_timezone = Timezone.from_raw(args.user_timezone)
        user_feature_flags: UserFeatureFlags = {}
        for enabled_feature in args.user_feature_flag_enabled:
            user_feature_flags[UserFeature(enabled_feature)] = True
        for disabled_feature in args.user_feature_flag_disable:
            user_feature_flags[UserFeature(disabled_feature)] = False
        auth_current_password = cast(PasswordPlain, args.current_password)
        auth_new_password = cast(PasswordNewPlain, args.new_password)
        auth_new_password_repeat = cast(PasswordNewPlain, args.new_password_repeat)
        workspace_name = WorkspaceName.from_raw(args.workspace_name)
        workspace_default_project_ref_id = EntityId.from_raw(
            args.workspace_default_project_ref_id
        )
        workspace_feature_flags: WorkspaceFeatureFlags = {}
        for enabled_feature in args.workspace_feature_flag_enabled:
            workspace_feature_flags[WorkspaceFeature(enabled_feature)] = True
        for disabled_feature in args.workspace_feature_flag_disable:
            workspace_feature_flags[WorkspaceFeature(disabled_feature)] = False

        session_info = self._session_storage.load()

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            ClearAllArgs(
                user_name=user_name,
                user_timezone=user_timezone,
                user_feature_flags=user_feature_flags,
                auth_current_password=auth_current_password,
                auth_new_password=auth_new_password,
                auth_new_password_repeat=auth_new_password_repeat,
                workspace_name=workspace_name,
                workspace_default_project_ref_id=workspace_default_project_ref_id,
                workspace_feature_flags=workspace_feature_flags,
            ),
        )
