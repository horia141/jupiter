"""The rules for skipping a recurring task."""

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import PrimitiveAtomicValueDatabaseDecoder, PrimitiveAtomicValueDatabaseEncoder


@value
class RecurringTaskSkipRule(AtomicValue[str]):
    """The rules for skipping a recurring task."""

    skip_rule: str

    def __str__(self) -> str:
        """Transform this to a string version."""
        return self.skip_rule


class RecurringTaskSkipRuleDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[RecurringTaskSkipRule]):

    def to_primitive(self, value: RecurringTaskSkipRule) -> Primitive:
        return value.skip_rule
    

class RecurringTaskSkipRuleDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[RecurringTaskSkipRule]):

    def from_raw_str(self, value: str) -> RecurringTaskSkipRule:
        return RecurringTaskSkipRule(value.strip().lower())
