"""Framework level elements for entity events."""
import dataclasses
import enum
import inspect
import typing
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Dict

from pendulum import Date, DateTime

from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.json import JSONValueType
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.value import Value

EventType = TypeVar('EventType', bound='Event')


@enum.unique
class EventKind(enum.Enum):
    """The kind of an event."""
    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    RESTORE = "restore"

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
    """An event for an aggregate root."""

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
                    if arg_name in ('self', 'source'):
                        # This is called from some sort of method of an aggregate root class and we're looking
                        # at this frame. There is a self and it's the aggregate root itself! Ditto don't need to
                        # map the source again.
                        continue
                    frame_args[arg_name] = args.locals[arg_name]
                for kwarg_name, kwargs_value in kwargs.items():
                    frame_args[kwarg_name] = kwargs_value
                new_event = \
                    cls(source=source, entity_version=entity_version, timestamp=timestamp, frame_args=frame_args)
                return new_event
            finally:
                del parent_frame
        finally:
            del frame

    def to_serializable_dict(self) -> JSONValueType:
        """Transform an event into a serialisation-ready dictionary."""
        def process_primitive(primitive: typing.Union[None, int, float, str, object], key: str) -> JSONValueType:
            if primitive is None:
                return primitive
            elif isinstance(primitive, int):
                return primitive
            elif isinstance(primitive, float):
                return primitive
            elif isinstance(primitive, str):
                return primitive
            elif isinstance(primitive, Date):
                return str(primitive)
            elif isinstance(primitive, DateTime):
                return str(primitive)
            elif isinstance(primitive, Enum):
                return process_primitive(primitive.value, key)
            elif isinstance(primitive, Value):
                return str(primitive)  # A bit of a hack really!
            elif dataclasses.is_dataclass(primitive):
                return {k: process_primitive(v, k) for k, v in dataclasses.asdict(primitive).items()}
            elif isinstance(primitive, list):
                return [process_primitive(p, key) for p in primitive]
            elif isinstance(primitive, dict):
                return {k: process_primitive(v, k) for k, v in primitive.items()}
            else:
                raise Exception(f"Invalid type for event field {key} of type {primitive.__class__.__name__}")
        serialized_frame_args = {}
        for the_key, the_value in self.frame_args.items():
            if isinstance(the_value, UpdateAction):
                if the_value.should_change:
                    serialized_frame_args[the_key] = process_primitive(the_value.value, the_key)
            else:
                serialized_frame_args[the_key] = process_primitive(the_value, the_key)
        return serialized_frame_args

    @property
    def kind(self) -> EventKind:
        """The kind of event this is."""
        raise NotImplementedError("Something went terribly wrong")
