"""Command for changint the feature flags for a user."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.user.change_feature_flags import (
    UserChangeFeatureFlagsUseCase,
)


class UserChangeFeatureFlags(LoggedInMutationCommand[UserChangeFeatureFlagsUseCase]):
    """Command for changint the feature flags for a user."""
