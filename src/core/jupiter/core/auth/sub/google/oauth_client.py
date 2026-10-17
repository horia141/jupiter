"""An oauth2 client."""

from typing import Final, cast

import httpx
import jwt
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from jupiter.core.auth.sub.google.google_auth_code import GoogleAuthCode
from jupiter.core.auth.sub.google.google_oauth_redirect_state import (
    GoogleOauthRedirectState,
)
from jupiter.core.auth.sub.google.id_token_claims import GoogleIdTokenClaims
from jupiter.core.auth.sub.google.oauth_token_response import GoogleOAuthTokenResponse
from jupiter.core.auth.sub.google.refresh_token_encrypted import (
    GoogleRefreshTokenEncrypted,
)
from jupiter.core.auth.sub.google.refresh_token_plain import GoogleRefreshTokenPlain
from jupiter.core.auth.sub.google.user_info import GoogleUserInfo
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

_GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
_GOOGLE_ISSUER = "https://accounts.google.com"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"  # nosec B105
_GOOGLE_AUTHORISATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
_GOOGLE_ID_TOKEN_ALGORITHMS = ["RS256"]


class GoogleRefreshTokenRevokedError(Exception):
    """Raised when Google rejects a refresh token (e.g. user revoked app access)."""


_cached_jwks_client: PyJWKClient | None = None


class GoogleOauthClient:
    """An oauth2 client."""

    _client_id: Final[str]
    _client_secret: Final[str]
    _refresh_token_encryption_key: Final[str]
    _realm_codec_registry: Final[RealmCodecRegistry]
    _client: Final[AsyncOAuth2Client]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token_encryption_key: str,
        realm_codec_registry: RealmCodecRegistry,
    ) -> None:
        """Initialize the oauth client."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token_encryption_key = refresh_token_encryption_key
        self._realm_codec_registry = realm_codec_registry
        self._client = AsyncOAuth2Client(
            client_id=self._client_id,
            client_secret=self._client_secret,
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
                GoogleOauthRedirectState, WebRealm
            ).encode(
                GoogleOauthRedirectState.new(
                    callback_success_url,
                    callback_failure_url,
                )
            ),
        )
        authorisation_url, _ = self._client.create_authorization_url(
            _GOOGLE_AUTHORISATION_URL,
            scope="openid email profile",
            access_type="offline",
            prompt="consent",
            redirect_uri=ready_url.the_url,
            state=state,
        )
        return URL(authorisation_url), state

    async def get_user_info(
        self,
        code: str,
        callback_uri: SystemUrl,
    ) -> GoogleUserInfo:
        """Exchange an authorisation code and return parsed Google user info."""
        return await self._get_user_info(code, callback_uri)

    async def get_user_info_from_native_code(self, code: str) -> GoogleUserInfo:
        """Exchange a ``serverAuthCode`` from the native sign in SDK.

        It has no redirect, and is exchanged with the same web client, so the ID
        token audience stays the same.
        """
        return await self._get_user_info(code, None)

    async def _get_user_info(
        self, code: str, callback_uri: SystemUrl | None
    ) -> GoogleUserInfo:
        try:
            token_raw = await self._exchange_code_for_tokens(code, callback_uri)
            token_response = self._realm_codec_registry.get_decoder(
                GoogleOAuthTokenResponse, WebRealm
            ).decode(token_raw)
            claims_raw = self._decode_google_id_token(token_response.id_token)
            claims = self._realm_codec_registry.get_decoder(
                GoogleIdTokenClaims, WebRealm
            ).decode(claims_raw)
        except RealmDecodingError as err:
            raise InputValidationError(str(err)) from err

        return GoogleUserInfo.from_oauth(
            token_response,
            claims,
            refresh_token_encryption_key=self._refresh_token_encryption_key,
        )

    async def sync_user_info_from_refresh_token(
        self, refresh_token: GoogleRefreshTokenEncrypted
    ) -> GoogleUserInfo:
        """Refresh access and return profile plus any rotated refresh token."""
        plain = refresh_token.to_plain(self._refresh_token_encryption_key)
        access_token, rotated_refresh_token = await self._exchange_refresh_token(plain)

        google_user_info = await self._fetch_user_info_with_access_token(access_token)

        encrypted_rotated: GoogleRefreshTokenEncrypted | None = None
        if rotated_refresh_token is not None:
            encrypted_rotated = GoogleRefreshTokenEncrypted.from_plain(
                rotated_refresh_token,
                self._refresh_token_encryption_key,
            )

        return GoogleUserInfo(
            google_subject_id=google_user_info.google_subject_id,
            email_address=google_user_info.email_address,
            user_name=google_user_info.user_name,
            verified=google_user_info.verified,
            encrypted_refresh_token=encrypted_rotated,
        )

    def cleared_refresh_token(self) -> GoogleRefreshTokenEncrypted:
        """An encrypted placeholder for a revoked refresh token."""
        return GoogleRefreshTokenEncrypted.from_plain(
            GoogleRefreshTokenPlain(""),
            self._refresh_token_encryption_key,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await cast(httpx.AsyncClient, self._client).aclose()

    async def _exchange_refresh_token(
        self, refresh_token: GoogleRefreshTokenPlain
    ) -> tuple[GoogleAuthCode, GoogleRefreshTokenPlain | None]:
        """Exchange a refresh token for an access token; optional rotated refresh token."""
        try:
            token_raw = await self._client.refresh_token(
                _GOOGLE_TOKEN_URL,
                refresh_token=refresh_token.token_raw,
            )
        except OAuthError as err:
            if err.error == "invalid_grant":
                raise GoogleRefreshTokenRevokedError(str(err)) from err
            raise

        token = cast(dict[str, object], token_raw)
        access_token = self._access_token_from_oauth_token_payload(token)

        rotated_refresh_token: GoogleRefreshTokenPlain | None = None
        new_refresh = token.get("refresh_token")
        if isinstance(new_refresh, str) and new_refresh:
            rotated_refresh_token = GoogleRefreshTokenPlain(new_refresh)

        return access_token, rotated_refresh_token

    async def _fetch_user_info_with_access_token(
        self, access_token: GoogleAuthCode
    ) -> GoogleUserInfo:
        """Fetch OpenID userinfo for an access token."""
        async with httpx.AsyncClient() as http:
            resp = await http.get(
                _GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token.code_raw}"},
            )
            if resp.status_code != 200:
                raise InputValidationError(
                    f"Google userinfo request failed with status {resp.status_code}"
                )
            profile = resp.json()

        try:
            claims = self._realm_codec_registry.get_decoder(
                GoogleIdTokenClaims, WebRealm
            ).decode(cast(dict[str, RealmThing], profile))
        except RealmDecodingError as err:
            raise InputValidationError(str(err)) from err

        return GoogleUserInfo.from_id_token_claims(claims)

    def _access_token_from_oauth_token_payload(
        self, token: dict[str, object]
    ) -> GoogleAuthCode:
        """Parse an access token from a Google OAuth token endpoint response."""
        raw_access_token = token.get("access_token")
        return self._realm_codec_registry.get_decoder(GoogleAuthCode, WebRealm).decode(
            cast(RealmThing, raw_access_token)
        )

    async def _exchange_code_for_tokens(
        self,
        code: str,
        callback_uri: SystemUrl | None,
    ) -> dict[str, RealmThing]:
        token = await self._client.fetch_token(
            _GOOGLE_TOKEN_URL,
            code=code,
            redirect_uri=callback_uri.the_url if callback_uri is not None else None,
        )
        return cast(dict[str, RealmThing], token)

    def _decode_google_id_token(self, id_token: str) -> dict[str, RealmThing]:
        try:
            return self._decode_google_id_token_with_jwks(id_token, _get_jwks_client())
        except jwt.InvalidTokenError:
            global _cached_jwks_client
            _cached_jwks_client = PyJWKClient(_GOOGLE_JWKS_URL)
            return self._decode_google_id_token_with_jwks(id_token, _cached_jwks_client)

    def _decode_google_id_token_with_jwks(
        self, id_token: str, jwks_client: PyJWKClient
    ) -> dict[str, RealmThing]:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        return cast(
            dict[str, RealmThing],
            jwt.decode(
                id_token,
                signing_key.key,
                algorithms=_GOOGLE_ID_TOKEN_ALGORITHMS,
                audience=self._client_id,
                issuer=_GOOGLE_ISSUER,
            ),
        )


def _get_jwks_client() -> PyJWKClient:
    global _cached_jwks_client
    if _cached_jwks_client is None:
        _cached_jwks_client = PyJWKClient(_GOOGLE_JWKS_URL)
    return _cached_jwks_client
