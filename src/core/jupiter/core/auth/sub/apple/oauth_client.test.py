"""Tests for Apple ID token claims, redirect state, and the client-secret JWT."""

import asyncio

import jupiter.core
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jupiter.core.auth.sub.apple.apple_oauth_redirect_state import (
    AppleOauthRedirectState,
    AppleOauthRedirectStateWebDecoder,
    AppleOauthRedirectStateWebEncoder,
)
from jupiter.core.auth.sub.apple.id_token_claims import AppleIdTokenClaims
from jupiter.core.auth.sub.apple.oauth_client import AppleOauthClient
from jupiter.core.auth.sub.apple.user_info import AppleUserInfo
from jupiter.core.common.email_address import EmailAddress
from jupiter.core.common.system_url import SystemUrl
from jupiter.core.users.name import UserName
from jupiter.framework.errors import InputValidationError
from jupiter.framework.realm.realm import WebRealm
from jupiter.framework.realm.standard import ModuleExplorerRealmCodecRegistry

_TEAM_ID = "TEAMID123"
_KEY_ID = "KEYID12345"
_SERVICES_ID = "com.example.thrive.service"
_NATIVE_CLIENT_ID = "com.example.thrive"


@pytest.fixture(scope="module")
def realm_codec_registry() -> ModuleExplorerRealmCodecRegistry:
    """Codec registry covering the core package."""
    return ModuleExplorerRealmCodecRegistry.build_from_module_root(jupiter.core)


def test_id_token_claims_accept_string_email_verified(
    realm_codec_registry: ModuleExplorerRealmCodecRegistry,
) -> None:
    """Apple sometimes returns email_verified and is_private_email as strings."""
    claims = realm_codec_registry.get_decoder(AppleIdTokenClaims, WebRealm).decode(
        {
            "sub": "001234.abcdef",
            "email": "ada@privaterelay.appleid.com",
            "email_verified": "true",
            "is_private_email": "true",
        }
    )

    assert isinstance(claims, AppleIdTokenClaims)
    assert claims.email_verified is True
    assert claims.is_private_email is True
    assert claims.sub.the_value == "001234.abcdef"


def test_id_token_claims_allow_missing_private_email(
    realm_codec_registry: ModuleExplorerRealmCodecRegistry,
) -> None:
    """is_private_email is optional on the ID token."""
    claims = realm_codec_registry.get_decoder(AppleIdTokenClaims, WebRealm).decode(
        {
            "sub": "001234.abcdef",
            "email": "ada@example.com",
            "email_verified": False,
        }
    )

    assert isinstance(claims, AppleIdTokenClaims)
    assert claims.email_verified is False
    assert claims.is_private_email is None


def test_missing_first_sign_in_name_falls_back_to_email_local_part() -> None:
    """Apple omits the name after the first authorisation."""
    email = EmailAddress("ada.lovelace@example.com")

    assert AppleUserInfo.user_name_from_apple_user_json(None, email) == UserName(
        "ada.lovelace"
    )
    assert AppleUserInfo.user_name_from_apple_user_json(
        '{"name":{"firstName":"Ada","lastName":"Lovelace"},"email":"ada@example.com"}',
        email,
    ) == UserName("Ada Lovelace")


def test_redirect_state_round_trip() -> None:
    """Encoded OAuth state decodes back to the same callback URLs."""
    state = AppleOauthRedirectState.new(
        SystemUrl(
            "https://app.example.com/app/lifecycle/init/apple/create-or-login-user"
        ),
        SystemUrl("https://app.example.com/app/lifecycle/login/local/login"),
    )

    encoded = AppleOauthRedirectStateWebEncoder().encode(state)
    assert isinstance(encoded, str)
    decoded = AppleOauthRedirectStateWebDecoder().decode(encoded)

    assert decoded.nonce == state.nonce
    assert decoded.callback_success_url == state.callback_success_url
    assert decoded.callback_failure_url == state.callback_failure_url


def test_client_secret_jwt_claims(
    realm_codec_registry: ModuleExplorerRealmCodecRegistry,
) -> None:
    """The client secret is an ES256 JWT with Apple's required claims."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    client = AppleOauthClient(
        team_id=_TEAM_ID,
        key_id=_KEY_ID,
        services_id=_SERVICES_ID,
        private_key_pem=pem.replace("\n", "\\n"),
        refresh_token_encryption_key="unused",  # nosec B106
        realm_codec_registry=realm_codec_registry,
        native_client_id=_NATIVE_CLIENT_ID,
    )

    token = client._client_secret(_SERVICES_ID)
    assert client._client_secret(_SERVICES_ID) == token

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "ES256"
    assert header["kid"] == _KEY_ID

    claims = jwt.decode(
        token,
        public_pem,
        algorithms=["ES256"],
        audience="https://appleid.apple.com",
    )
    assert claims["iss"] == _TEAM_ID
    assert claims["sub"] == _SERVICES_ID
    assert claims["exp"] - claims["iat"] == 60 * 60

    # The app signs in as its bundle id, so its secret names that as the subject.
    native_token = client._client_secret(_NATIVE_CLIENT_ID)
    assert native_token != token
    native_claims = jwt.decode(
        native_token,
        public_pem,
        algorithms=["ES256"],
        audience="https://appleid.apple.com",
    )
    assert native_claims["sub"] == _NATIVE_CLIENT_ID


def test_native_code_is_refused_without_a_native_client_id(
    realm_codec_registry: ModuleExplorerRealmCodecRegistry,
) -> None:
    """A code with no redirect URI can't be exchanged unless the app id is set."""
    client = AppleOauthClient(
        team_id=_TEAM_ID,
        key_id=_KEY_ID,
        services_id=_SERVICES_ID,
        private_key_pem="unused",  # nosec B106
        refresh_token_encryption_key="unused",  # nosec B106
        realm_codec_registry=realm_codec_registry,
    )

    with pytest.raises(InputValidationError):
        asyncio.run(client.get_user_info_from_native_code("some-code", None))
