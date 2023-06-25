"""Session storage for the CLI app."""
import json
from pathlib import Path
from typing import Final

from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.framework.secure import secure_class
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder


class SessionInfoNotFoundError(Exception):
    """Error raised when a session is not found."""


@dataclass
class SessionInfo:
    """Information about the session."""

    auth_token_ext: AuthTokenExt


@secure_class
class SessionStorage:
    """Session storage for the CLI app."""

    _session_info_path: Final[Path]

    def __init__(self, session_info_path: Path) -> None:
        """Constructor."""
        self._session_info_path = session_info_path

    def load(self) -> SessionInfo:
        """Load session data."""
        try:
            with self._session_info_path.open() as f:
                session_str = f.read()
                session_dict = json.loads(session_str)
                return SessionInfo(**session_dict)
        except FileNotFoundError as err:
            raise SessionInfoNotFoundError("No session info found") from err

    def load_optional(self) -> SessionInfo | None:
        """Load session data, and return null if it isn't there."""
        try:
            with self._session_info_path.open() as f:
                session_str = f.read()
                session_dict = json.loads(session_str)
                return SessionInfo(**session_dict)
        except FileNotFoundError:
            return None

    def store(self, session: SessionInfo) -> None:
        """Store session data."""
        with self._session_info_path.open("w") as f:
            session_dict = json.dumps(session, indent=4, default=pydantic_encoder)
            f.write(session_dict)

    def clear(self) -> None:
        """Clear data stored in session."""
        try:
            self._session_info_path.unlink()
        except FileNotFoundError:
            pass
