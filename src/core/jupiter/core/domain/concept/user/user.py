"""A user of jupiter."""

import abc

from jupiter.core.domain.application.gamification.score_log import ScoreLog
from jupiter.core.domain.concept.auth.auth import Auth
from jupiter.core.domain.concept.user.avatar import Avatar
from jupiter.core.domain.concept.user.user_category import UserCategory
from jupiter.core.domain.concept.user.user_name import UserName
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.core.timezone import UTC, Timezone
from jupiter.core.domain.features import (
    UserFeature,
    UserFeatureFlags,
    UserFeatureFlagsControls,
)
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsOne,
    IsRefId,
    RootEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    RootEntityRepository,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class User(RootEntity):
    """A user of jupiter."""

    category: UserCategory
    email_address: EmailAddress
    name: UserName
    avatar: Avatar
    timezone: Timezone
    feature_flags: UserFeatureFlags

    auth = ContainsOne(Auth, user_ref_id=IsRefId())
    score_log = ContainsOne(ScoreLog, user_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_standard_user(
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
            category=UserCategory.STANDARD,
            email_address=email_address,
            name=name,
            avatar=Avatar.from_user_name(name),
            timezone=timezone,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta=feature_flags, current_feature_flags={}
            ),
        )

    @staticmethod
    @create_entity_action
    def new_app_store_review_user(
        ctx: DomainContext,
        email_address: EmailAddress,
        name: UserName,
        feature_flag_controls: UserFeatureFlagsControls,
    ) -> "User":
        """Create a new user."""
        return User._create(
            ctx,
            category=UserCategory.APP_STORE_REVIEW,
            email_address=email_address,
            name=name,
            avatar=Avatar.from_user_name(name),
            timezone=UTC,
            feature_flags=feature_flag_controls.validate_and_complete(
                feature_flags_delta={}, current_feature_flags={}
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

    @property
    def should_go_through_onboarding_flow(self) -> bool:
        """Return whether the user should go through the onboarding flow."""
        return self.category == UserCategory.STANDARD


class UserAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a user already exists."""


class UserNotFoundError(EntityNotFoundError):
    """Error raised when a user does not exist."""


class UserRepository(RootEntityRepository[User], abc.ABC):
    """A repository for users."""

    @abc.abstractmethod
    async def load_by_email_address(self, email_address: EmailAddress) -> User:
        """Load a user given their email address."""
