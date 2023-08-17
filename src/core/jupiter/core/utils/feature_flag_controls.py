"""Utilities for feature controls."""
from typing import Tuple

from jupiter.core.domain.features import (
    HOSTED_GLOBAL_WORKSPACE_FEATURE_FLAGS_CONTROLS,
    LOCAL_WORKSPACE_FEATURE_FLAGS_CONTROLS,
    USER_FEATURE_FLAGS_CONTROLS,
    UserFeatureFlagsControls,
    WorkspaceFeatureFlagsControls,
)
from jupiter.core.domain.hosting import Hosting
from jupiter.core.utils.global_properties import GlobalProperties


def infer_feature_flag_controls(
    global_properties: GlobalProperties,
) -> Tuple[UserFeatureFlagsControls, WorkspaceFeatureFlagsControls]:
    """Infer the feature flags controls to use, based on magick."""
    if global_properties.hosting == Hosting.LOCAL:
        return USER_FEATURE_FLAGS_CONTROLS, LOCAL_WORKSPACE_FEATURE_FLAGS_CONTROLS
    else:
        return (
            USER_FEATURE_FLAGS_CONTROLS,
            HOSTED_GLOBAL_WORKSPACE_FEATURE_FLAGS_CONTROLS,
        )
