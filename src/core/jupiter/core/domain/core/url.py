"""An URL in this domain."""
from functools import total_ordering

import validators
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value


@value
@total_ordering
class URL(AtomicValue):
    """A URL in this domain."""

    the_url: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_url = self._clean_the_url(self.the_url)

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "URL":
        """Validate and clean a url."""
        if not isinstance(value, str):
            raise InputValidationError("Expected url to be a string")

        return URL(URL._clean_the_url(value))

    def to_primitive(self) -> Primitive:
        return self.the_url

    def __lt__(self, other: object) -> bool:
        """Compare this with another."""
        if not isinstance(other, URL):
            raise Exception(f"Cannot compare an URL {other.__class__.__name__}")
        return self.the_url < other.the_url

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.the_url

    @staticmethod
    def _clean_the_url(url_raw: str) -> str:
        url_str: str = url_raw.strip()

        validation_result = validators.url(url_str)
        if validation_result is not True:
            raise InputValidationError(f"Invalid URL '{url_raw}'")
        return url_str
