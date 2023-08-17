"""Even features are expressed here."""
import enum
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Final, Iterable

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value


class FeatureUnavailableError(Exception):
    """Exception raised when a feature is unavailable."""

    _error_str: Final[str]

    def __init__(self, feature_or_str: "WorkspaceFeature | str"):
        """Constructor."""
        super().__init__()
        self._error_str = (
            (f"Feature {feature_or_str.value} is not available in this workspace")
            if isinstance(feature_or_str, WorkspaceFeature)
            else feature_or_str
        )

    def __str__(self) -> str:
        """Form a string representation here."""
        return self._error_str


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
                raise InputValidationError(
                    f"Cannot disable {property_name} because it should always be on"
                )
        elif (
            self == FeatureControl.ALWAYS_OFF_TECH
            or self == FeatureControl.ALWAYS_OFF_HOSTING
        ):
            if property_value is True:
                raise InputValidationError(
                    f"Cannot enable {property_name} because this environment doesn't support it"
                )

        return property_value


@enum.unique
class UserFeature(enum.Enum):
    """A particular feature of a Jupiter user."""

    GAMIFICATION_SCORES = "gamification-scores"

    @staticmethod
    @lru_cache(maxsize=1)
    def all_values() -> Iterable[str]:
        """The possible values for user features."""
        return list(p.value for p in UserFeature)


UserFeatureFlags = Dict[UserFeature, bool]


@dataclass
class UserFeatureFlagsControls(Value):
    """Feature settings controls for the user."""

    controls: Dict[UserFeature, FeatureControl]

    def validate_and_complete(
        self,
        feature_flags_delta: UserFeatureFlags,
        current_feature_flags: UserFeatureFlags,
    ) -> UserFeatureFlags:
        """Validates a set of feature flags and also provides a complete set."""
        checked_feature_flags: UserFeatureFlags = {}

        for feature, control in self.controls.items():
            if feature in feature_flags_delta:
                checked_feature_flags[feature] = control.check(
                    feature.value, feature_flags_delta[feature]
                )
            elif feature in current_feature_flags:
                checked_feature_flags[feature] = current_feature_flags[feature]
            else:
                checked_feature_flags[feature] = control.standard_flag

        return checked_feature_flags


@enum.unique
class WorkspaceFeature(enum.Enum):
    """A particular feature of a Jupiter workspace."""

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
        """The possible values for workspace features."""
        return list(p.value for p in WorkspaceFeature)


WorkspaceFeatureFlags = Dict[WorkspaceFeature, bool]


@dataclass
class WorkspaceFeatureFlagsControls(Value):
    """Feature settings controls for the workspace."""

    controls: Dict[WorkspaceFeature, FeatureControl]

    def validate_and_complete(
        self,
        feature_flags_delta: WorkspaceFeatureFlags,
        current_feature_flags: WorkspaceFeatureFlags,
    ) -> WorkspaceFeatureFlags:
        """Validates a set of feature flags and also provides a complete set."""
        checked_feature_flags: WorkspaceFeatureFlags = {}

        for feature, control in self.controls.items():
            if feature in feature_flags_delta:
                checked_feature_flags[feature] = control.check(
                    feature.value, feature_flags_delta[feature]
                )
            elif feature in current_feature_flags:
                checked_feature_flags[feature] = current_feature_flags[feature]
            else:
                checked_feature_flags[feature] = control.standard_flag

        return checked_feature_flags


BASIC_USER_FEATURE_FLAGS = {UserFeature.GAMIFICATION_SCORES: True}


USER_FEATURE_FLAGS_CONTROLS = UserFeatureFlagsControls(
    {UserFeature.GAMIFICATION_SCORES: FeatureControl.USER}
)


BASIC_WORKSPACE_FEATURE_FLAGS = {
    WorkspaceFeature.INBOX_TASKS: True,
    WorkspaceFeature.HABITS: True,
    WorkspaceFeature.CHORES: False,
    WorkspaceFeature.BIG_PLANS: False,
    WorkspaceFeature.VACATIONS: False,
    WorkspaceFeature.PROJECTS: False,
    WorkspaceFeature.SMART_LISTS: False,
    WorkspaceFeature.METRICS: False,
    WorkspaceFeature.PERSONS: False,
    WorkspaceFeature.SLACK_TASKS: False,
    WorkspaceFeature.EMAIL_TASKS: False,
}


HOSTED_GLOBAL_WORKSPACE_FEATURE_FLAGS_CONTROLS = WorkspaceFeatureFlagsControls(
    {
        WorkspaceFeature.INBOX_TASKS: FeatureControl.ALWAYS_ON,
        WorkspaceFeature.HABITS: FeatureControl.USER,
        WorkspaceFeature.CHORES: FeatureControl.USER,
        WorkspaceFeature.BIG_PLANS: FeatureControl.USER,
        WorkspaceFeature.VACATIONS: FeatureControl.USER,
        WorkspaceFeature.PROJECTS: FeatureControl.USER,
        WorkspaceFeature.SMART_LISTS: FeatureControl.USER,
        WorkspaceFeature.METRICS: FeatureControl.USER,
        WorkspaceFeature.PERSONS: FeatureControl.USER,
        WorkspaceFeature.SLACK_TASKS: FeatureControl.ALWAYS_OFF_TECH,
        WorkspaceFeature.EMAIL_TASKS: FeatureControl.ALWAYS_OFF_TECH,
    }
)


LOCAL_WORKSPACE_FEATURE_FLAGS_CONTROLS = WorkspaceFeatureFlagsControls(
    {
        WorkspaceFeature.INBOX_TASKS: FeatureControl.ALWAYS_ON,
        WorkspaceFeature.HABITS: FeatureControl.USER,
        WorkspaceFeature.CHORES: FeatureControl.USER,
        WorkspaceFeature.BIG_PLANS: FeatureControl.USER,
        WorkspaceFeature.VACATIONS: FeatureControl.USER,
        WorkspaceFeature.PROJECTS: FeatureControl.USER,
        WorkspaceFeature.SMART_LISTS: FeatureControl.USER,
        WorkspaceFeature.METRICS: FeatureControl.USER,
        WorkspaceFeature.PERSONS: FeatureControl.USER,
        WorkspaceFeature.SLACK_TASKS: FeatureControl.ALWAYS_OFF_HOSTING,
        WorkspaceFeature.EMAIL_TASKS: FeatureControl.ALWAYS_OFF_HOSTING,
    }
)
