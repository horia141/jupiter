"""An authentication token allows for secure and fast authentication across a session."""
from typing import ClassVar, Dict
from jupiter.core.framework.realm import CliRealm, WebRealm, only_in_realm

import jwt
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.value import SecretValue, secret_value

_ALGORITHM = "HS256"


class ExpiredAuthTokenError(Exception):
    """Exception thrown when an auth token is expired."""


class InvalidAuthTokenError(Exception):
    """Exception thrown when an auth token is invalid in some way (malformed, or fake)."""


@secret_value
@only_in_realm(CliRealm, WebRealm)
class AuthToken(SecretValue):
    """An authentication token allows for secure and fast authentication across a session."""

    _AUDIENCE_GENERAL: ClassVar[str] = "general"
    _AUDIENCE_GENERAL_DURATION: ClassVar[Dict[str, int]] = {"months": 1}
    _AUDIENCE_PROGRESS_REPORTER: ClassVar[str] = "progress-reporter"
    _AUDIENCE_PROGRESS_REPORTER_DURATION: ClassVar[Dict[str, int]] = {"minutes": 10}

    user_ref_id: EntityId
    issue_time: Timestamp
    expiration_time: Timestamp
    audience: str
    auth_token_str: str

    @staticmethod
    def new_for_general(
        secret: str, user_ref_id: EntityId, right_now: Timestamp
    ) -> "AuthToken":
        """Create a new auth token useful for general modifications."""
        return AuthToken._new_for_audience(
            secret,
            user_ref_id,
            right_now,
            AuthToken._AUDIENCE_GENERAL,
            AuthToken._AUDIENCE_GENERAL_DURATION,
        )

    @staticmethod
    def new_for_progress_reporter(
        secret: str, user_ref_id: EntityId, right_now: Timestamp
    ) -> "AuthToken":
        """Create a new auth token useful for progress reporter updates."""
        return AuthToken._new_for_audience(
            secret,
            user_ref_id,
            right_now,
            AuthToken._AUDIENCE_PROGRESS_REPORTER,
            AuthToken._AUDIENCE_PROGRESS_REPORTER_DURATION,
        )

    @staticmethod
    def _new_for_audience(
        secret: str,
        user_ref_id: EntityId,
        right_now: Timestamp,
        audience: str,
        duration: Dict[str, int],
    ) -> "AuthToken":
        """Constract a new auth token."""
        issue_time = right_now
        expiration_time = Timestamp.from_date_and_time(
            right_now.as_datetime().add(**duration)
        )
        auth_token_str = jwt.encode(
            {
                "user_ref_id": str(user_ref_id),
                "iat": issue_time.as_datetime(),
                "exp": expiration_time.as_datetime(),
                "aud": [audience],
            },
            secret,
            _ALGORITHM,
        )

        return AuthToken(
            user_ref_id=user_ref_id,
            issue_time=issue_time,
            expiration_time=expiration_time,
            audience=audience,
            auth_token_str=auth_token_str,
        )

    @staticmethod
    def from_raw_general(secret: str, auth_token_raw: str) -> "AuthToken":
        """Extract and verify an auth token for general modifications."""
        return AuthToken._from_raw_audience(
            secret, auth_token_raw, AuthToken._AUDIENCE_GENERAL
        )

    @staticmethod
    def from_raw_progress_reporter(secret: str, auth_token_raw: str) -> "AuthToken":
        """Extract and verify an auth token for general modifications."""
        return AuthToken._from_raw_audience(
            secret, auth_token_raw, AuthToken._AUDIENCE_PROGRESS_REPORTER
        )

    @staticmethod
    def _from_raw_audience(
        secret: str, auth_token_raw: str, audience: str
    ) -> "AuthToken":
        """Extract and verify an auth token given as string."""
        try:
            auth_token_json = jwt.decode(
                auth_token_raw,
                secret,
                [_ALGORITHM],
                {
                    "verify_signature": True,
                    "require": ["user_ref_id", "iat", "exp", "aud"],
                    "verify_exp": True,
                    "verify_iat": True,
                },
                audience=audience,
            )

            user_ref_id = EntityId.from_raw(auth_token_json["user_ref_id"])
            issue_time = Timestamp.from_unix_timestamp(auth_token_json["iat"])
            expiration_time = Timestamp.from_unix_timestamp(auth_token_json["exp"])

            return AuthToken(
                user_ref_id=user_ref_id,
                issue_time=issue_time,
                expiration_time=expiration_time,
                audience=audience,
                auth_token_str=auth_token_raw,
            )
        except jwt.ExpiredSignatureError as err:
            raise ExpiredAuthTokenError("Auth token has expired") from err
        except (
            jwt.InvalidTokenError,
            jwt.DecodeError,
            jwt.InvalidSignatureError,
            jwt.InvalidAudienceError,
        ) as err:
            raise InvalidAuthTokenError("Auth token is invalid") from err

    def to_ext(self) -> AuthTokenExt:
        """Return the external representation of the auth token."""
        return AuthTokenExt(self.auth_token_str)
