"""Framework level elements for entity events."""
import enum
from dataclasses import dataclass

from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.realm import DomainThing
from jupiter.core.framework.value import EnumValue, enum_value


@enum.unique
class EventKind(enum.Enum):
    """The kind of an event."""

    CREATE = "Created"
    UPDATE = "Updated"
    ARCHIVE = "Archived"


@enum_value
class EventSource(EnumValue):
    """The source of the modification which this event records."""

    CLI = "cli"
    WEB = "web"
    SLACK = "slack"
    EMAIL = "email"
    GC_CRON = "gc-cron"
    GEN_CRON = "gen-cron"
    SCHEDULE_EXTERNAL_SYNC_CRON = "schedule-external-sync-cron"


@dataclass(frozen=True)
class Event:
    """An event for an entity."""

    source: EventSource
    entity_version: int
    timestamp: Timestamp
    frame_args: dict[str, tuple[DomainThing, type[DomainThing]]]
    kind: EventKind
    name: str
