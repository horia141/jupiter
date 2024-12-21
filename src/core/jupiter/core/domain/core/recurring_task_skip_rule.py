"""The rules for skipping a recurring task."""

from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@value
class RecurringTaskSkipRule(AtomicValue[str]):
    """The rules for skipping a recurring task."""

    skip_rule: str

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.skip_rule


class RecurringTaskSkipRuleDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[RecurringTaskSkipRule]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: RecurringTaskSkipRule) -> Primitive:
        """Encode to a database primitive."""
        return value.skip_rule


class RecurringTaskSkipRuleDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[RecurringTaskSkipRule]
):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> RecurringTaskSkipRule:
        """Decode from a raw string."""
        return RecurringTaskSkipRule(value.strip().lower())
