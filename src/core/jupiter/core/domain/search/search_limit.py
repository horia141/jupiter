"""A search limit parameter for searches."""


from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseDecoder, PrimitiveAtomicValueDatabaseEncoder

_MAX_QUERY_LIMIT = 1000


@value
class SearchLimit(AtomicValue[int]):
    """A search limit parameter for searches."""

    the_limit: int

    def __str__(self) -> str:
        """Transform this to a string version."""
        return str(self.the_limit)


class SearchLimitDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[SearchLimit]):

    def to_primitive(self, value: SearchLimit) -> Primitive:
        return value.the_limit
    

class SearchLimitDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[SearchLimit]):

    def from_raw_int(self, value: int) -> SearchLimit:
        if value < 1:
            raise InputValidationError("Expected limit to be a positive number")

        if value > _MAX_QUERY_LIMIT:
            raise InputValidationError(
                f"Expected limit to be smaller than {_MAX_QUERY_LIMIT}"
            )

        return SearchLimit(value)
