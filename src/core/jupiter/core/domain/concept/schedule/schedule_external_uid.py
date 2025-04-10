"""An external UID for a schedule."""

from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.value import AtomicValue, value
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


@value
class ScheduleExternalUid(AtomicValue[str]):
    """An external UID for a schedule."""

    the_uid: str

    @staticmethod
    def from_string(value: str) -> "ScheduleExternalUid":
        """Create from a string."""
        if not value:
            raise InputValidationError("External UID cannot be empty")
        return ScheduleExternalUid(value)


class ScheduleExternalUidDatabaseEncoder(
    PrimitiveAtomicValueDatabaseEncoder[ScheduleExternalUid]
):
    """Encode to a database primitive."""

    def to_primitive(self, value: ScheduleExternalUid) -> str:
        """Encode to a raw string."""
        return value.the_uid


class ScheduleExternalUidDatabaseDecoder(
    PrimitiveAtomicValueDatabaseDecoder[ScheduleExternalUid]
):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> ScheduleExternalUid:
        """Decode from a raw string."""
        return ScheduleExternalUid.from_string(value)
