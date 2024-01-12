"""A search limit parameter for searches."""

from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value

_MAX_QUERY_LIMIT = 1000


@value
class SearchLimit(AtomicValue):
    """A search limit parameter for searches."""

    the_limit: int

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_limit = self._clean_the_limit(self.the_limit)

    @staticmethod
    def from_raw(limit_raw: Optional[int]) -> "SearchLimit":
        """Validate and clean the search limit."""
        if not limit_raw:
            raise InputValidationError("Expected limit to be non null.")

        return SearchLimit(SearchLimit._clean_the_limit(limit_raw))

    def to_primitive(self) -> Primitive:
        return self.the_limit

    @property
    def as_int(self) -> int:
        """Return an integer representation of the limit."""
        return self.the_limit

    def __str__(self) -> str:
        """Transform this to a string version."""
        return str(self.the_limit)

    @staticmethod
    def _clean_the_limit(limit_raw: int) -> int:
        if limit_raw < 1:
            raise InputValidationError("Expected limit to be a positive number")

        if limit_raw > _MAX_QUERY_LIMIT:
            raise InputValidationError(
                f"Expected limit to be smaller than {_MAX_QUERY_LIMIT}"
            )

        return limit_raw
