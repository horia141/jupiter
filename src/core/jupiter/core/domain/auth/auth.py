"""Authentication information associated with a user."""

from jupiter.core.domain.auth.password_hash import PasswordHash
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.auth.recovery_token_hash import RecoveryTokenHash
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ParentLink,
    StubEntity,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.realm import DatabaseRealm, only_in_realm
from jupiter.core.framework.secure import secure_class


class IncorrectPasswordError(Exception):
    """Exception raised when an invalid password is provided."""


class IncorrectRecoveryTokenError(Exception):
    """Exception raised when an incorrect recovery token is provided."""


@entity
@secure_class
@only_in_realm(DatabaseRealm)
class Auth(StubEntity):
    """Authentication information associated with a user."""

    user: ParentLink
    password_hash: PasswordHash
    recovery_token_hash: RecoveryTokenHash

    @staticmethod
    def new_auth(
        ctx: DomainContext,
        user_ref_id: EntityId,
        password: PasswordNewPlain,
        password_repeat: PasswordNewPlain,
    ) -> tuple["Auth", RecoveryTokenPlain]:
        """Create a new auth for a user."""
        if password != password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        password_hash = PasswordHash.from_new_plain(password)
        recovery_token = RecoveryTokenPlain.new_recovery_token()
        recovery_token_hash = RecoveryTokenHash.from_plain(recovery_token)

        auth = Auth._new_auth_with_receovery_token(
            ctx,
            user_ref_id=user_ref_id,
            password_hash=password_hash,
            recovery_token_hash=recovery_token_hash,
        )

        return (auth, recovery_token)

    @staticmethod
    @create_entity_action
    def _new_auth_with_receovery_token(
        ctx: DomainContext,
        user_ref_id: EntityId,
        password_hash: PasswordHash,
        recovery_token_hash: RecoveryTokenHash,
    ) -> "Auth":
        """Create a new auth for a user."""
        return Auth._create(
            ctx,
            user=ParentLink(user_ref_id),
            password_hash=password_hash,
            recovery_token_hash=recovery_token_hash,
        )

    @update_entity_action
    def change_password(
        self,
        ctx: DomainContext,
        current_password: PasswordPlain,
        new_password: PasswordNewPlain,
        new_password_repeat: PasswordNewPlain,
    ) -> "Auth":
        """Change the password for a user at the authentication level."""
        if not self.password_hash.check_against(current_password):
            raise IncorrectPasswordError("Invalid password")
        if new_password != new_password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        new_password_hash = PasswordHash.from_new_plain(new_password)

        return self._new_version(
            ctx,
            password_hash=new_password_hash,
        )

    def reset_password(
        self,
        ctx: DomainContext,
        recovery_token: RecoveryTokenPlain,
        new_password: PasswordNewPlain,
        new_password_repeat: PasswordNewPlain,
    ) -> tuple["Auth", RecoveryTokenPlain]:
        """Reset the password for a user by using a recovery token."""
        if not self.recovery_token_hash.check_against(recovery_token):
            raise IncorrectRecoveryTokenError("Invalid recovery token")
        if new_password != new_password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        new_password_hash = PasswordHash.from_new_plain(new_password)
        new_recovery_token = RecoveryTokenPlain.new_recovery_token()
        new_recovery_token_hash = RecoveryTokenHash.from_plain(new_recovery_token)

        new_auth = self._reset_password_and_recovery_token(
            ctx,
            new_password_hash=new_password_hash,
            new_recovery_token_hash=new_recovery_token_hash,
        )

        return (new_auth, new_recovery_token)

    @update_entity_action
    def _reset_password_and_recovery_token(
        self,
        ctx: DomainContext,
        new_password_hash: PasswordHash,
        new_recovery_token_hash: RecoveryTokenHash,
    ) -> "Auth":
        """Reset the password and recovery token for a user."""
        return self._new_version(
            ctx,
            password_hash=new_password_hash,
            recovery_token_hash=new_recovery_token_hash,
        )

    def check_password_against(self, password: PasswordPlain) -> bool:
        """Check a password for this auth."""
        return self.password_hash.check_against(password)
