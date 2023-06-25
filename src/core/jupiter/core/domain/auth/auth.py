"""Authentication information associated with a user."""
from dataclasses import dataclass
from typing import Tuple

from jupiter.core.domain.auth.password_hash import PasswordHash
from jupiter.core.domain.auth.password_new_plain import PasswordNewPlain
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.auth.recovery_token_hash import RecoveryTokenHash
from jupiter.core.domain.auth.recovery_token_plain import RecoveryTokenPlain
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, StubEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.secure import secure_class


class IncorrectPasswordError(Exception):
    """Exception raised when an invalid password is provided."""


class IncorrectRecoveryTokenError(Exception):
    """Exception raised when an incorrect recovery token is provided."""


@dataclass
@secure_class
class Auth(StubEntity):
    """Authentication information associated with a user."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class ChangePassword(Entity.Updated):
        """Change the password at the request of the user."""

    @dataclass
    class ResetPassword(Entity.Updated):
        """Reset the password of the user by way of a recovery token."""

    user_ref_id: EntityId
    password_hash: PasswordHash
    recovery_token_hash: RecoveryTokenHash

    @staticmethod
    def new_auth(
        user_ref_id: EntityId,
        password: PasswordNewPlain,
        password_repeat: PasswordNewPlain,
        source: EventSource,
        created_time: Timestamp,
    ) -> Tuple["Auth", RecoveryTokenPlain]:
        """Create a new auth for a user."""
        if password != password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        password_hash = PasswordHash.from_new_plain(password)
        recovery_token = RecoveryTokenPlain.new_recovery_token()
        recovery_token_hash = RecoveryTokenHash.from_plain(recovery_token)

        auth = Auth(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            last_modified_time=created_time,
            archived_time=None,
            events=[
                Auth.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                ),
            ],
            user_ref_id=user_ref_id,
            password_hash=password_hash,
            recovery_token_hash=recovery_token_hash,
        )

        return (auth, recovery_token)

    def change_password(
        self,
        current_password: PasswordPlain,
        new_password: PasswordNewPlain,
        new_password_repeat: PasswordNewPlain,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Auth":
        """Change the password for a user at the authentication level."""
        if not self.password_hash.check_against(current_password):
            raise IncorrectPasswordError("Invalid password")
        if new_password != new_password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        new_password_hash = PasswordHash.from_new_plain(new_password)

        return self._new_version(
            password_hash=new_password_hash,
            new_event=Auth.ChangePassword.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    def reset_password(
        self,
        recovery_token: RecoveryTokenPlain,
        new_password: PasswordNewPlain,
        new_password_repeat: PasswordNewPlain,
        source: EventSource,
        modification_time: Timestamp,
    ) -> Tuple["Auth", RecoveryTokenPlain]:
        """Reset the password for a user by using a recovery token."""
        if not self.recovery_token_hash.check_against(recovery_token):
            raise IncorrectRecoveryTokenError("Invalid recovery token")
        if new_password != new_password_repeat:
            raise InputValidationError("Expected the password and repeat to match")

        new_password_hash = PasswordHash.from_new_plain(new_password)
        new_recovery_token = RecoveryTokenPlain.new_recovery_token()
        new_recovery_token_hash = RecoveryTokenHash.from_plain(new_recovery_token)

        new_auth = self._new_version(
            password_hash=new_password_hash,
            recovery_token_hash=new_recovery_token_hash,
            new_event=Auth.ResetPassword.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

        return (new_auth, new_recovery_token)

    def check_password_against(self, password: PasswordPlain) -> bool:
        """Check a password for this auth."""
        return self.password_hash.check_against(password)
