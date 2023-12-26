"""A user of Jupiter."""
from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.timezone import Timezone
from jupiter.core.domain.features import (
    UserFeature,
    UserFeatureFlags,
    UserFeatureFlagsControls,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.user.avatar import Avatar
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsOne,
    IsRefId,
    RootEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class User(RootEntity):
    """A user of Jupiter."""

    email_address: EmailAddress
    name: UserName
    avatar: Avatar
    timezone: Timezone
    feature_flags: UserFeatureFlags

    auth = ContainsOne(Auth, user_ref_id=IsRefId())
    score_log = ContainsOne(ScoreLog, user_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_user(
        ctx: DomainContext,
        email_address: EmailAddress,
        name: UserName,
        timezone: Timezone,
        feature_flag_controls: UserFeatureFlagsControls,
        feature_flags: UserFeatureFlags,
    ) -> "User":
        """Create a new user."""
        return User._create(
            ctx,
            email_address=email_address,
            name=name,
            avatar=Avatar.from_user_name(name),
            timezone=timezone,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags, current_feature_flags={}
            ),
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[UserName],
        timezone: UpdateAction[Timezone],
    ) -> "User":
        """Update properties of the user."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            avatar=name.transform(lambda n: Avatar.from_user_name(n)).or_else(
                self.avatar
            ),
            timezone=timezone.or_else(self.timezone),
        )

    @update_entity_action
    def change_feature_flags(
        self,
        ctx: DomainContext,
        feature_flag_controls: UserFeatureFlagsControls,
        feature_flags: UserFeatureFlags,
    ) -> "User":
        """Change the feature settings for this user."""
        return self._new_version(
            ctx,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags,
                current_feature_flags=self.feature_flags,
            ),
        )

    def is_feature_available(self, feature: UserFeature) -> bool:
        """Check if a feature is available for this user."""
        return self.feature_flags[feature]
