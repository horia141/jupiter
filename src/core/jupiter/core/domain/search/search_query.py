"""A search query parameter for searches."""


from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value


@value
class SearchQuery(AtomicValue):
    """A search query parameter for searches."""

    the_query: str

    def __post_init__(self) -> None:
        """Validate after pydantic construction."""
        self.the_query = self._clean_the_query(self.the_query)

    @classmethod
    def base_type_hack(cls) -> type[Primitive]:
        return str

    @classmethod
    def from_raw(cls, value: Primitive) -> "SearchQuery":
        """Validate and clean the search query."""
        if not isinstance(value, str):
            raise InputValidationError("Expected query to be a string")

        return SearchQuery(SearchQuery._clean_the_query(value))

    def to_primitive(self) -> Primitive:
        return self.the_query

    def __str__(self) -> str:
        """Transform this to a string version."""
        return str(self.the_query)

    @staticmethod
    def _clean_the_query(query_raw: str) -> str:
        query_nows = query_raw.strip()

        if len(query_nows) == 0:
            raise InputValidationError("Expected query to be non empty.")

        return query_nows
