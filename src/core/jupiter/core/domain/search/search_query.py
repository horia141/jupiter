"""A search query parameter for searches."""


from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@value
class SearchQuery(AtomicValue[str]):
    """A search query parameter for searches."""

    the_query: str

    def __str__(self) -> str:
        """Transform this to a string version."""
        return str(self.the_query)


class SearchQueryDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[SearchQuery]):
    def to_primitive(self, value: SearchQuery) -> Primitive:
        return value.the_query


class SearchQueryDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[SearchQuery]):
    def from_raw_str(self, primitive: str) -> SearchQuery:
        query_nows = primitive.strip()

        if len(query_nows) == 0:
            raise InputValidationError("Expected query to be non empty.")

        return SearchQuery(query_nows)
