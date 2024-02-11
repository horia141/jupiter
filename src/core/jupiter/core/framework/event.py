"""Framework level elements for entity events."""
import enum
from dataclasses import dataclass
from typing import Dict, cast

from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.realm import DatabaseRealm, RealmCodecRegistry, RealmThing
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.utils import is_thing_ish_type
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

    def to_serializable_dict(self, realm_codec_registry: RealmCodecRegistry) -> RealmThing:
        """Transform an event into a serialisation-ready dictionary."""
        serialized_frame_args = {}
        for the_key, the_value in self.frame_args.items():
            if not is_thing_ish_type(the_value.__class__):
                raise Exception(f"The domain should deal with things, but found {the_value.__class__}")
            encoder = realm_codec_registry.get_encoder(the_value.__class__, DatabaseRealm)
            serialized_frame_args[the_key] = encoder.encode(cast(Thing, the_value))
        return serialized_frame_args
