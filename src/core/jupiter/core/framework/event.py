"""Framework level elements for entity events."""
import enum
from dataclasses import dataclass
from typing import Dict

from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.value import EnumValue, enum_value


@enum.unique
class EventKind(enum.Enum):
    """The kind of an event."""

    CREATE = "Created"
    UPDATE = "Updated"
    ARCHIVE = "Archived"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@enum_value
class EventSource(EnumValue):
    """The source of the modification which this event records."""

    CLI = "cli"
    WEB = "web"
    SLACK = "slack"
    EMAIL = "email"
    GC_CRON = "gc-cron"
    GEN_CRON = "gen-cron"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@dataclass
class Event:
    """An event for an entity."""

    source: EventSource
    entity_version: int
    timestamp: Timestamp
    frame_args: Dict[str, object]
    kind: EventKind
    name: str
