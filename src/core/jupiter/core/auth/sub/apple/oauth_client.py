"""An OAuth2 client for Sign in with Apple."""

import re
import time
from typing import Final, cast

import httpx
import jwt
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from jupiter.core.auth.sub.apple.apple_oauth_redirect_state import (
    AppleOauthRedirectState,
)
from jupiter.core.auth.sub.apple.id_token_claims import AppleIdTokenClaims
from jupiter.core.auth.sub.apple.oauth_token_response import AppleOAuthTokenResponse
from jupiter.core.auth.sub.apple.refresh_token_encrypted import (
    AppleRefreshTokenEncrypted,
)
from jupiter.core.auth.sub.apple.refresh_token_plain import AppleRefreshTokenPlain
from jupiter.core.auth.sub.apple.user_info import AppleUserInfo
from jupiter.core.common.system_url import SystemUrl
from jupiter.core.common.url import URL
from jupiter.framework.errors import InputValidationError
from jupiter.framework.realm.realm import (
    RealmCodecRegistry,
    RealmDecodingError,
    RealmThing,
    WebRealm,
)
from jwt import PyJWKClient

_APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
_APPLE_ISSUER = "https://appleid.apple.com"
_APPLE_TOKEN_URL = "https://appleid.apple.com/auth/token"  # nosec B105
_APPLE_AUTHORISATION_URL = "https://appleid.apple.com/auth/authorize"
_APPLE_REVOKE_URL = "https://appleid.apple.com/auth/revoke"
_APPLE_ID_TOKEN_ALGORITHMS = ["RS256"]
_CLIENT_SECRET_LIFETIME_SECONDS = 60 * 60
_CLIENT_SECRET_RENEW_BEFORE_SECONDS = 60


_PEM_BODY_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----(.*?)-----END [A-Z ]*PRIVATE KEY-----", re.S
)


def _normalize_pem(raw: str) -> str:
    r"""Rebuild a well-formed PKCS8 PEM from whatever an env var mangled it into.

    Handles surrounding quotes, literal ``\n`` sequences, CRLFs, newlines
    collapsed into spaces, and a missing BEGIN/END header.
    """
    pem = raw.strip().strip("'\"").replace("\\n", "\n").replace("\r", "")
    match = _PEM_BODY_RE.search(pem)
    body = match.group(1) if match else pem
    body = re.sub(r"\s+", "", body)
    lines = [body[i : i + 64] for i in range(0, len(body), 64)]
    return "\n".join(
        ["-----BEGIN PRIVATE KEY-----", *lines, "-----END PRIVATE KEY-----", ""]
    )


class AppleRefreshTokenRevokedError(Exception):
    """Raised when Apple rejects a refresh token (e.g. the user revoked the app)."""


_cached_jwks_client: PyJWKClient | None = None


class AppleOauthClient:
    """An OAuth2 client for Sign in with Apple."""

    _team_id: Final[str]
    _key_id: Final[str]
    _services_id: Final[str]
    _private_key_pem: Final[str]
    _refresh_token_encryption_key: Final[str]
    _realm_codec_registry: Final[RealmCodecRegistry]
    _client: Final[AsyncOAuth2Client]
    _cached_client_secret: str | None
    _cached_client_secret_exp: int

    def __init__(
        self,
        team_id: str,
        key_id: str,
        services_id: str,
        private_key_pem: str,
        refresh_token_encryption_key: str,
        realm_codec_registry: RealmCodecRegistry,
    ) -> None:
        """Initialize the OAuth client.

        The PEM is kept as text and parsed only when a client secret is needed,
        so a placeholder key does not stop the process from starting.
        """
        self._team_id = team_id
        self._key_id = key_id
        self._services_id = services_id
        self._private_key_pem = private_key_pem
        self._refresh_token_encryption_key = refresh_token_encryption_key
        self._realm_codec_registry = realm_codec_registry
        self._cached_client_secret = None
        self._cached_client_secret_exp = 0
        self._client = AsyncOAuth2Client(
            client_id=self._services_id,
            token_endpoint_auth_method="client_secret_post",  # nosec B106
        )

    def get_authorisation_url(
        self,
        ready_url: SystemUrl,
        callback_success_url: SystemUrl,
        callback_failure_url: SystemUrl,
    ) -> tuple[URL, str]:
        """Get the authorisation url and OAuth state."""
        state = cast(
            str,
            self._realm_codec_registry.get_encoder(
                AppleOauthRedirectState, WebRealm
            ).encode(
                AppleOauthRedirectState.new(
                    callback_success_url,
                    callback_failure_url,
                )
            ),
        )
        authorisation_url, _ = self._client.create_authorization_url(
            _APPLE_AUTHORISATION_URL,
            scope="name email",
            response_mode="form_post",
            redirect_uri=ready_url.the_url,
            state=state,
        )
        return URL(authorisation_url), state

    async def get_user_info(
        self,
        code: str,
        callback_uri: SystemUrl,
        user_json: str | None,
    ) -> AppleUserInfo:
        """Exchange an authorisation code and return parsed Apple user info."""
        try:
            token_raw = await self._exchange_code_for_tokens(code, callback_uri)
            token_response = self._realm_codec_registry.get_decoder(
                AppleOAuthTokenResponse, WebRealm
            ).decode(token_raw)
            claims_raw = self._decode_apple_id_token(token_response.id_token)
            claims = self._realm_codec_registry.get_decoder(
                AppleIdTokenClaims, WebRealm
            ).decode(claims_raw)
        except RealmDecodingError as err:
            raise InputValidationError(str(err)) from err

        return AppleUserInfo.from_oauth(
            token_response,
            claims,
            user_json=user_json,
            refresh_token_encryption_key=self._refresh_token_encryption_key,
        )

    async def validate_refresh_token(
        self, refresh_token: AppleRefreshTokenEncrypted
    ) -> AppleRefreshTokenEncrypted | None:
        """Confirm a refresh token is still accepted, returning a rotation if any.

        Apple has no userinfo endpoint, so this only checks the token. A new
        refresh token is returned when Apple rotates it.
        """
        plain = refresh_token.to_plain(self._refresh_token_encryption_key)
        rotated = await self._exchange_refresh_token(plain)
        if rotated is None:
            return None
        return AppleRefreshTokenEncrypted.from_plain(
            rotated,
            self._refresh_token_encryption_key,
        )

    async def revoke_refresh_token(
        self, refresh_token: AppleRefreshTokenEncrypted
    ) -> None:
        """Revoke a refresh token at Apple. Required when an account is deleted."""
        plain = refresh_token.to_plain(self._refresh_token_encryption_key)
        if not plain.token_raw:
            return
        async with httpx.AsyncClient() as http:
            resp = await http.post(
                _APPLE_REVOKE_URL,
                data={
                    "client_id": self._services_id,
                    "client_secret": self._client_secret(),
                    "token": plain.token_raw,
                    "token_type_hint": "refresh_token",  # nosec B105
                },
            )
            if resp.status_code != 200:
                raise InputValidationError(
                    f"Apple token revoke failed with status {resp.status_code}"
                )

    def cleared_refresh_token(self) -> AppleRefreshTokenEncrypted:
        """An encrypted placeholder for a revoked refresh token."""
        return AppleRefreshTokenEncrypted.from_plain(
            AppleRefreshTokenPlain(""),
            self._refresh_token_encryption_key,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await cast(httpx.AsyncClient, self._client).aclose()

    def _client_secret(self) -> str:
        """An ES256 JWT Apple accepts as ``client_secret``, cached under an hour."""
        now = int(time.time())
        if (
            self._cached_client_secret is not None
            and self._cached_client_secret_exp - _CLIENT_SECRET_RENEW_BEFORE_SECONDS
            > now
        ):
            return self._cached_client_secret

        exp = now + _CLIENT_SECRET_LIFETIME_SECONDS
        token = jwt.encode(
            {
                "iss": self._team_id,
                "iat": now,
                "exp": exp,
                "aud": _APPLE_ISSUER,
                "sub": self._services_id,
            },
            self._private_key(),
            algorithm="ES256",
            headers={"kid": self._key_id, "alg": "ES256"},
        )
        self._cached_client_secret = token
        self._cached_client_secret_exp = exp
        return token

    def _private_key(self) -> EllipticCurvePrivateKey:
        """Parse the .p8 PEM, turning escaped newlines from env vars into real ones."""
        pem = _normalize_pem(self._private_key_pem)
        try:
            key = load_pem_private_key(pem.encode(), password=None)
        except ValueError as err:
            raise InputValidationError(
                "Apple private key is not a valid PEM (.p8) file"
            ) from err
        if not isinstance(key, EllipticCurvePrivateKey):
            raise InputValidationError("Apple private key must be an EC private key")
        return key

    async def _exchange_refresh_token(
        self, refresh_token: AppleRefreshTokenPlain
    ) -> AppleRefreshTokenPlain | None:
        """Exchange a refresh token; return a rotated refresh token when Apple sends one."""
        self._client.client_secret = self._client_secret()
        try:
            token_raw = await self._client.refresh_token(
                _APPLE_TOKEN_URL,
                refresh_token=refresh_token.token_raw,
            )
        except OAuthError as err:
            if err.error == "invalid_grant":
                raise AppleRefreshTokenRevokedError(str(err)) from err
            raise

        token = cast(dict[str, object], token_raw)
        new_refresh = token.get("refresh_token")
        if isinstance(new_refresh, str) and new_refresh:
            return AppleRefreshTokenPlain(new_refresh)
        return None

    async def _exchange_code_for_tokens(
        self,
        code: str,
        callback_uri: SystemUrl,
    ) -> dict[str, RealmThing]:
        self._client.client_secret = self._client_secret()
        token = await self._client.fetch_token(
            _APPLE_TOKEN_URL,
            code=code,
            redirect_uri=callback_uri.the_url,
        )
        return cast(dict[str, RealmThing], token)

    def _decode_apple_id_token(self, id_token: str) -> dict[str, RealmThing]:
        try:
            return self._decode_apple_id_token_with_jwks(id_token, _get_jwks_client())
        except jwt.InvalidTokenError:
            global _cached_jwks_client
            _cached_jwks_client = PyJWKClient(_APPLE_JWKS_URL)
            return self._decode_apple_id_token_with_jwks(id_token, _cached_jwks_client)

    def _decode_apple_id_token_with_jwks(
        self, id_token: str, jwks_client: PyJWKClient
    ) -> dict[str, RealmThing]:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        return cast(
            dict[str, RealmThing],
            jwt.decode(
                id_token,
                signing_key.key,
                algorithms=_APPLE_ID_TOKEN_ALGORITHMS,
                audience=self._services_id,
                issuer=_APPLE_ISSUER,
            ),
        )


def _get_jwks_client() -> PyJWKClient:
    global _cached_jwks_client
    if _cached_jwks_client is None:
        _cached_jwks_client = PyJWKClient(_APPLE_JWKS_URL)
    return _cached_jwks_client
