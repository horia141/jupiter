"""The source of a journal entry."""
import enum
from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class JournalSource(EnumValue):
    """The source of a journal entry."""

    USER = "user"
    RECURRING = "recurring"
