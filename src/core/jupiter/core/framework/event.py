"""Framework level elements for entity events."""
import enum
from dataclasses import dataclass
from typing import Dict

from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.json import JSONDictType, process_primitive_to_json
from jupiter.core.framework.update_action import UpdateAction


@enum.unique
class EventKind(enum.Enum):
    """The kind of an event."""

    CREATE = "Created"
    UPDATE = "Updated"
    ARCHIVE = "Archived"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@enum.unique
class EventSource(enum.Enum):
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

    def to_serializable_dict(self) -> JSONDictType:
        """Transform an event into a serialisation-ready dictionary."""
        serialized_frame_args = {}
        for the_key, the_value in self.frame_args.items():
            if isinstance(the_value, UpdateAction):
                if the_value.should_change:
                    serialized_frame_args[the_key] = process_primitive_to_json(
                        the_value.just_the_value,
                        the_key,
                    )
            else:
                serialized_frame_args[the_key] = process_primitive_to_json(
                    the_value,
                    the_key,
                )
        return serialized_frame_args
