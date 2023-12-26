"""A search query parameter for searches."""

from typing import Optional

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import Value, value


@value
class SearchQuery(Value):
    """A search query parameter for searches."""

    the_query: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_query = self._clean_the_query(self.the_query)

    @staticmethod
    def from_raw(query_raw: Optional[str]) -> "SearchQuery":
        """Validate and clean the search query."""
        if not query_raw:
            raise InputValidationError("Expected query to be non null.")

        return SearchQuery(SearchQuery._clean_the_query(query_raw))

    def __str__(self) -> str:
        """Transform this to a string version."""
        return str(self.the_query)

    @staticmethod
    def _clean_the_query(query_raw: str) -> str:
        query_nows = query_raw.strip()

        if len(query_nows) == 0:
            raise InputValidationError("Expected query to be non empty.")

        return query_nows
