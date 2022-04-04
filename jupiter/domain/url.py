"""An URL in this domain."""
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional
from urllib.parse import urlparse

from jupiter.framework.errors import InputValidationError
from jupiter.framework.value import Value


@dataclass(frozen=True)
@total_ordering
class URL(Value):
    """An URL in this domain."""

    _the_url: str

    @staticmethod
    def from_raw(url_raw: Optional[str]) -> "URL":
        """Validate and clean a url."""
        if not url_raw:
            raise InputValidationError("Expected url to be non-null")

        url_str: str = url_raw.strip()

        try:
            return URL(urlparse(url_str).geturl())
        except ValueError as err:
            raise InputValidationError(f"Invalid URL '{url_raw}'") from err

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, URL):
            raise Exception(f"Cannot compare an URL {other.__class__.__name__}")
        return self._the_url < other._the_url

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self._the_url
