from jupiter.core.domain.app import AppVersion
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.primitive import Primitive
from jupiter.core.use_cases.infra.realms import (
    PrimitiveAtomicValueDatabaseDecoder,
    PrimitiveAtomicValueDatabaseEncoder,
)


class AppVersionDatabaseEncoder(PrimitiveAtomicValueDatabaseEncoder[AppVersion]):
    """Encode to a database primitive."""

    def to_primitive(self, value: AppVersion) -> Primitive:
        """Encode to a database primitive."""
        return value.the_version


class AppVersionDatabaseDecoder(PrimitiveAtomicValueDatabaseDecoder[AppVersion]):
    """Decode from a database primitive."""

    def from_raw_str(self, value: str) -> AppVersion:
        """Decode from a raw string."""
        version = value.strip()
        # Test that it matches {major}.{minor}.{patch} version.
        version_parts = version.split(".")
        if len(version_parts) != 3:
            raise InputValidationError(f"Expected a version, but got {version}")
        major, minor, patch = version_parts
        if not major.isdigit() or not minor.isdigit() or not patch.isdigit():
            raise InputValidationError(f"Expected a version, but got {version}")
        return AppVersion(value)
