"""Utilities for feature controls."""
from jupiter.core.domain.features import (
    HOSTED_GLOBAL_FEATURE_FLAGS_CONTROLS,
    LOCAL_FEATURE_FLAGS_CONTROLS,
    FeatureFlagsControls,
)
from jupiter.core.domain.hosting import Hosting
from jupiter.core.utils.global_properties import GlobalProperties


def infer_feature_flag_controls(
    global_properties: GlobalProperties,
) -> FeatureFlagsControls:
    """Infer the feature flags controls to use, based on magick."""
    if global_properties.hosting == Hosting.LOCAL:
        return LOCAL_FEATURE_FLAGS_CONTROLS
    else:
        return HOSTED_GLOBAL_FEATURE_FLAGS_CONTROLS
