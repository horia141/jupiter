"""Command for changint the feature flags for a workspace."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.workspaces.change_feature_flags import (
    WorkspaceChangeFeatureFlagsUseCase,
)


class WorkspaceChangeFeatureFlags(
    LoggedInMutationCommand[WorkspaceChangeFeatureFlagsUseCase]
):
    """Command for changint the feature flags for a workspace."""
