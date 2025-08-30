"""The reason why an entity was archived."""

from jupiter.core.framework.value import EnumValue, enum_value


@enum_value
class ArchivalReason(EnumValue):
    """The reason why an entity was archived."""

    USER = "user"
    GC = "gc"
    SYNC = "sync"
