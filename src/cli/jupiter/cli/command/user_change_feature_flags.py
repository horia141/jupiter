"""Command for changint the feature flags for a user."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.features import UserFeature, UserFeatureFlags
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.user.change_feature_flags import (
    UserChangeFeatureFlagsArgs,
    UserChangeFeatureFlagsUseCase,
)


class UserChangeFeatureFlags(LoggedInMutationCommand[UserChangeFeatureFlagsUseCase]):
    """Command for changint the feature flags for a user."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "user-change-feature-flags"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the user feature flags"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--feature",
            dest="user_feature_flag_enabled",
            default=[],
            action="append",
            choices=UserFeature.all_values(),
        )
        parser.add_argument(
            "--no-feature",
            dest="user_feature_flag_disable",
            default=[],
            action="append",
            choices=UserFeature.all_values(),
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        feature_flags: UserFeatureFlags = {}
        for enabled_feature in args.user_feature_flag_enabled:
            feature_flags[UserFeature(enabled_feature)] = True
        for disabled_feature in args.user_feature_flag_disable:
            feature_flags[UserFeature(disabled_feature)] = False

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            UserChangeFeatureFlagsArgs(feature_flags=feature_flags),
        )
