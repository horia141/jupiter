"""Command for changint the feature flags for a workspace."""
from argparse import ArgumentParser, Namespace

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.cli.session_storage import SessionInfo
from jupiter.core.domain.features import Feature, FeatureFlags
from jupiter.core.use_cases.infra.use_cases import AppLoggedInUseCaseSession
from jupiter.core.use_cases.workspaces.change_feature_flags import (
    WorkspaceChangeFeatureFlagsArgs,
    WorkspaceChangeFeatureFlagsUseCase,
)


class WorkspaceChangeFeatureFlags(
    LoggedInMutationCommand[WorkspaceChangeFeatureFlagsUseCase]
):
    """Command for changint the feature flags for a workspace."""

    @staticmethod
    def name() -> str:
        """The name of the command."""
        return "workspace-change-feature-flags"

    @staticmethod
    def description() -> str:
        """The description of the command."""
        return "Change the workspace feature flags"

    def build_parser(self, parser: ArgumentParser) -> None:
        """Construct a argparse parser for the command."""
        parser.add_argument(
            "--feature",
            dest="workspace_feature_flag_enabled",
            default=[],
            action="append",
            choices=Feature.all_values(),
        )
        parser.add_argument(
            "--no-feature",
            dest="workspace_feature_flag_disable",
            default=[],
            action="append",
            choices=Feature.all_values(),
        )

    async def _run(
        self,
        session_info: SessionInfo,
        args: Namespace,
    ) -> None:
        """Callback to execute when the command is invoked."""
        feature_flags: FeatureFlags = {}
        for enabled_feature in args.workspace_feature_flag_enabled:
            feature_flags[Feature(enabled_feature)] = True
        for disabled_feature in args.workspace_feature_flag_disable:
            feature_flags[Feature(disabled_feature)] = False

        await self._use_case.execute(
            AppLoggedInUseCaseSession(session_info.auth_token_ext),
            WorkspaceChangeFeatureFlagsArgs(feature_flags=feature_flags),
        )