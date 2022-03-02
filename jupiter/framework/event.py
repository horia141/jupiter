"""Framework level elements for entity events."""
import enum
import inspect
import typing
from dataclasses import dataclass
from typing import TypeVar, Dict

from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONDictType, process_primitive_to_json
from jupiter.framework.update_action import UpdateAction

EventType = TypeVar('EventType', bound='Event')


@enum.unique
class EventKind(enum.Enum):
    """The kind of an event."""
    CREATE = "Created"
    UPDATE = "Updated"
    ARCHIVE = "Archived"
    RESTORE = "Restored"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@enum.unique
class EventSource(enum.Enum):
    """The source of the modification which this event records."""
    CLI = "cli"
    NOTION = "notion"

    def to_db(self) -> str:
        """A database appropriate form of this enum."""
        return str(self.value)


@dataclass(frozen=True)
class Event:
    """An event for an entity."""

    source: EventSource
    entity_version: int
    timestamp: Timestamp
    frame_args: Dict[str, object]

    @classmethod
    def make_event_from_frame_args(
            cls: typing.Type[EventType], source: EventSource, entity_version: int, timestamp: Timestamp,
            **kwargs: object) -> EventType:
        """Construct the data for an event from the arguments of the method which calls this one."""
        frame = inspect.currentframe()
        if frame is None:
            raise Exception("There's no recovery from stuff like this - part one")

        try:
            parent_frame = frame.f_back
            if parent_frame is None:
                raise Exception("There's no recovery from stuff like this - part two")

            try:
                args = inspect.getargvalues(parent_frame)  # pylint: disable=deprecated-method
                frame_args = {}
                for arg_name in args.args:
                    if arg_name in ('self', 'source', 'event_type'):
                        # This is called from some sort of method of an entity class and we're looking
                        # at this frame. There is a self and it's the entity itself! Ditto don't need to
                        # map the source again. Nor the special `event_type'.
                        continue
                    frame_args[arg_name] = args.locals[arg_name]
                for kwarg_name, kwargs_value in kwargs.items():
                    frame_args[kwarg_name] = kwargs_value
                new_event = \
                    cls(source=source, entity_version=entity_version + 1, timestamp=timestamp, frame_args=frame_args)
                return new_event
            finally:
                del parent_frame
        finally:
            del frame

    def to_serializable_dict(self) -> JSONDictType:
        """Transform an event into a serialisation-ready dictionary."""
        serialized_frame_args = {}
        for the_key, the_value in self.frame_args.items():
            if isinstance(the_value, UpdateAction):
                if the_value.should_change:
                    serialized_frame_args[the_key] = process_primitive_to_json(the_value.value, the_key)
            else:
                serialized_frame_args[the_key] = process_primitive_to_json(the_value, the_key)
        return serialized_frame_args

    @property
    def kind(self) -> EventKind:
        """The kind of event this is."""
        raise NotImplementedError("Something went terribly wrong")
