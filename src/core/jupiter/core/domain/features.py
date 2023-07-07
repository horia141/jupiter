"""Even features are expressed here."""
import enum
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value


@enum.unique
class Feature(enum.Enum):
    """A particular feature of Jupiter."""

    INBOX_TASKS = "inbox-tasks"
    HABITS = "habits"
    CHORES = "chores"
    BIG_PLANS = "big-plans"
    VACATIONS = "vacations"
    PROJECTS = "projects"
    SMART_LISTS = "smart-lists"
    METRICS = "metrics"
    PERSONS = "persons"
    SLACK_TASKS = "slack-tasks"
    EMAIL_TASKS = "email-tasks"

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for difficulties."""
        return list(p.value for p in Feature)


FeatureFlags = Dict[Feature, bool]


@enum.unique
class FeatureControl(enum.Enum):
    """The level of control allowed for a particular feature."""

    # Feature can't be turned off by the user
    ALWAYS_ON = "always-on"
    # Feature can't be turned on by the user because we're having tech issues
    ALWAYS_OFF_TECH = "always-off-tech"
    # Feature can't be turned on by the user because it doesn't make sense in the hosting mode
    ALWAYS_OFF_HOSTING = "always-off-hosting"
    # Feature can be set by the user
    USER = "user"

    @property
    def standard_flag(self) -> bool:
        """The standard value for a feature flag controlled by this feature control."""
        return self == FeatureControl.ALWAYS_ON or self == FeatureControl.USER

    def check(self, property_name: str, property_value: bool) -> bool:
        """Verify if the property can be set."""
        if self == FeatureControl.ALWAYS_ON:
            if property_value is False:
                raise InputValidationError(f"Cannot disable {property_name}")
        elif (
            self == FeatureControl.ALWAYS_OFF_TECH
            or self == FeatureControl.ALWAYS_OFF_HOSTING
        ):
            if property_value is True:
                raise InputValidationError(f"Cannot enable {property_name}")

        return property_value


@dataclass
class FeatureFlagsControls(Value):
    """Feature settings controls for the workspace."""

    controls: Dict[Feature, FeatureControl]

    def build_standard_flags(self) -> FeatureFlags:
        """Construct a set of standard feature flags for the given features and controls."""
        return {f: c.standard_flag for f, c in self.controls.items()}

    def validate_and_complete_feature_flags(
        self, feature_flags: FeatureFlags
    ) -> FeatureFlags:
        """Validates a set of feature flags and also provides a complete set."""
        print(feature_flags)
        checked_feature_flags: FeatureFlags = {}

        for feature, control in self.controls.items():
            if feature not in feature_flags:
                checked_feature_flags[feature] = control.standard_flag
            else:
                checked_feature_flags[feature] = control.check(
                    str(feature), feature_flags[feature]
                )
        print(checked_feature_flags)

        return checked_feature_flags


HOSTED_GLOBAL_FEATURE_FLAGS_CONTROLS = FeatureFlagsControls(
    {
        Feature.INBOX_TASKS: FeatureControl.ALWAYS_ON,
        Feature.HABITS: FeatureControl.USER,
        Feature.CHORES: FeatureControl.USER,
        Feature.BIG_PLANS: FeatureControl.USER,
        Feature.VACATIONS: FeatureControl.USER,
        Feature.PROJECTS: FeatureControl.USER,
        Feature.SMART_LISTS: FeatureControl.USER,
        Feature.METRICS: FeatureControl.USER,
        Feature.PERSONS: FeatureControl.USER,
        Feature.SLACK_TASKS: FeatureControl.ALWAYS_OFF_TECH,
        Feature.EMAIL_TASKS: FeatureControl.ALWAYS_OFF_TECH,
    }
)

LOCAL_FEATURE_FLAGS_CONTROLS = FeatureFlagsControls(
    {
        Feature.INBOX_TASKS: FeatureControl.ALWAYS_ON,
        Feature.HABITS: FeatureControl.USER,
        Feature.CHORES: FeatureControl.USER,
        Feature.BIG_PLANS: FeatureControl.USER,
        Feature.VACATIONS: FeatureControl.USER,
        Feature.PROJECTS: FeatureControl.USER,
        Feature.SMART_LISTS: FeatureControl.USER,
        Feature.METRICS: FeatureControl.USER,
        Feature.PERSONS: FeatureControl.USER,
        Feature.SLACK_TASKS: FeatureControl.ALWAYS_OFF_HOSTING,
        Feature.EMAIL_TASKS: FeatureControl.ALWAYS_OFF_HOSTING,
    }
)

DEVMODE_FEATURE_FLAGS_CONTROLS = FeatureFlagsControls(
    {
        Feature.INBOX_TASKS: FeatureControl.ALWAYS_ON,
        Feature.HABITS: FeatureControl.USER,
        Feature.CHORES: FeatureControl.USER,
        Feature.BIG_PLANS: FeatureControl.USER,
        Feature.VACATIONS: FeatureControl.USER,
        Feature.PROJECTS: FeatureControl.USER,
        Feature.SMART_LISTS: FeatureControl.USER,
        Feature.METRICS: FeatureControl.USER,
        Feature.PERSONS: FeatureControl.USER,
        Feature.SLACK_TASKS: FeatureControl.USER,
        Feature.EMAIL_TASKS: FeatureControl.USER,
    }
)
