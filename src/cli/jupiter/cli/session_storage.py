"""Session storage for the CLI app."""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from jupiter.core.domain.concept.auth.auth_token_ext import AuthTokenExt
from jupiter.core.framework.realm import RealmCodecRegistry, RealmDecodingError
from jupiter.core.framework.secure import secure_class


class SessionInfoNotFoundError(Exception):
    """Error raised when a session is not found."""


@dataclass(frozen=True)
class SessionInfo:
    """Information about the session."""

    auth_token_ext: AuthTokenExt


@secure_class
class SessionStorage:
    """Session storage for the CLI app."""

    _session_info_path: Final[Path]
    _realm_codec_registry: Final[RealmCodecRegistry]

    def __init__(
        self, session_info_path: Path, realm_codec_registry: RealmCodecRegistry
    ) -> None:
        """Constructor."""
        self._session_info_path = session_info_path
        self._realm_codec_registry = realm_codec_registry

    def load(self) -> SessionInfo:
        """Load session data."""
        try:
            with self._session_info_path.open() as f:
                session_str = f.read()
                session_dict = json.loads(session_str)
                if "auth_token_ext" not in session_dict:
                    raise SessionInfoNotFoundError("No auth token found")
                auth_token_ext = self._realm_codec_registry.db_decode(
                    AuthTokenExt, session_dict["auth_token_ext"]
                )
                return SessionInfo(auth_token_ext=auth_token_ext)
        except (FileNotFoundError, RealmDecodingError) as err:
            raise SessionInfoNotFoundError("No session info found") from err

    def load_optional(self) -> SessionInfo | None:
        """Load session data, and return null if it isn't there."""
        try:
            with self._session_info_path.open() as f:
                session_str = f.read()
                session_dict = json.loads(session_str)
                if "auth_token_ext" not in session_dict:
                    return None
                auth_token_ext = self._realm_codec_registry.db_decode(
                    AuthTokenExt, session_dict["auth_token_ext"]
                )
                return SessionInfo(auth_token_ext=auth_token_ext)
        except (FileNotFoundError, RealmDecodingError):
            return None

    def store(self, session: SessionInfo) -> None:
        """Store session data."""
        with self._session_info_path.open("w") as f:
            session_dict = json.dumps(
                {
                    "auth_token_ext": self._realm_codec_registry.db_encode(
                        session.auth_token_ext
                    ),
                },
                indent=4,
            )
            f.write(session_dict)

    def clear(self) -> None:
        """Clear data stored in session."""
        try:
            self._session_info_path.unlink()
        except FileNotFoundError:
            pass
