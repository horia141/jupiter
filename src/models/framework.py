"""Helpers for working with entities."""
import abc
import dataclasses
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic, List, Optional, Iterator, Iterable, Final

import typing

from pendulum import Date, DateTime

from models.basic import EntityId, Timestamp, BasicValidator
from utils.storage import JSONValueType

BAD_REF_ID = EntityId("bad-entity-id")


UpdateActionType = TypeVar('UpdateActionType')


class UpdateAction(Generic[UpdateActionType]):
    """The update action for a field."""

    _should_change: Final[bool]
    _value: Optional[UpdateActionType]

    def __init__(self, should_change: bool, value: Optional[UpdateActionType] = None) -> None:
        """Constructor."""
        self._should_change = should_change
        self._value = value

    @staticmethod
    def do_nothing() -> 'UpdateAction[UpdateActionType]':
        """An update action where nothing needs to happen."""
        return UpdateAction[UpdateActionType](should_change=False)

    @staticmethod
    def change_to(value: UpdateActionType) -> 'UpdateAction[UpdateActionType]':
        """An update action where the value needs to be changed to a new value."""
        return UpdateAction[UpdateActionType](should_change=True, value=value)

    @property
    def should_change(self) -> bool:
        """Whether the value should change or not."""
        return self._should_change

    @property
    def value(self) -> UpdateActionType:
        """Return the value if it exists."""
        if not self._should_change:
            raise Exception("Trying to get the value when it's not there")
        return typing.cast(UpdateActionType, self._value)


@dataclass(frozen=True)
class Event:
    """The base class for all events."""

    timestamp: Timestamp

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
                return BasicValidator.adate_to_str(primitive)
            elif isinstance(primitive, DateTime):
                return BasicValidator.adate_to_str(primitive)
            elif isinstance(primitive, Enum):
                return process_primitive(primitive.value, key)
            elif isinstance(primitive, UpdateAction):
                return {
                    "should_change": primitive.should_change,
                    "value": process_primitive(primitive.value, key) if primitive.should_change else None
                }
            elif dataclasses.is_dataclass(primitive):
                return {key: process_primitive(value, key) for key, value in dataclasses.asdict(primitive).items()}
            else:
                raise Exception(f"Invalid type for event field {key} of type {primitive.__class__.__name__} -> {key}")
        return process_primitive(self, "root")


@dataclass()
class AggregateRoot:
    """The base class for all aggregate roots."""

    @dataclass(frozen=True)
    class Created(Event):
        """Created event."""

    @dataclass(frozen=True)
    class Archived(Event):
        """Archived event."""

    @dataclass(frozen=True)
    class Unarchived(Event):
        """Unarchived event."""

    _ref_id: EntityId
    _archived: bool
    _created_time: Timestamp
    _last_modified_time: Timestamp
    _archived_time: Optional[Timestamp]
    _events: List[Event]

    def assign_ref_id(self, ref_id: EntityId) -> None:
        """Assign a ref id to the root."""
        self._ref_id = ref_id

    def mark_archived(self, archived_time: Timestamp) -> None:
        """Archive the root."""
        self._archived = True
        self._archived_time = archived_time
        self.record_event(AggregateRoot.Archived(timestamp=archived_time))

    def change_archived(self, archived: bool, archived_time: Timestamp) -> None:
        """Change the archival status."""
        if self._archived == archived:
            return
        elif not self._archived and archived:
            self._archived = True
            self._archived_time = archived_time
            self.record_event(AggregateRoot.Archived(timestamp=archived_time))
        elif self._archived and not archived:
            self._archived = False
            self._archived_time = None
            self.record_event(AggregateRoot.Unarchived(timestamp=archived_time))
        else:
            return

    def record_event(self, event: Event) -> None:
        """Record an event on the root."""
        self._last_modified_time = event.timestamp
        self._events.append(event)

    @property
    def ref_id(self) -> EntityId:
        """The ref id."""
        return self._ref_id

    @property
    def archived(self) -> bool:
        """The archivation status."""
        return self._archived

    @property
    def created_time(self) -> Timestamp:
        """The creation time."""
        return self._created_time

    @property
    def last_modified_time(self) -> Timestamp:
        """The last modified time."""
        return self._last_modified_time

    @property
    def archived_time(self) -> Optional[Timestamp]:
        """The archived time."""
        return self._archived_time

    @property
    def events(self) -> Iterable[Event]:
        """The events for a particular root."""
        return self._events


CommandArgs = TypeVar('CommandArgs')
CommandResult = TypeVar('CommandResult')


class Command(Generic[CommandArgs, CommandResult], abc.ABC):
    """A command."""

    @abc.abstractmethod
    def execute(self, args: CommandArgs) -> CommandResult:
        """Execute the command's action."""


class Repository(abc.ABC):
    """A repository."""


UnitOfWorkType = TypeVar('UnitOfWorkType', bound='UnitOfWork')


class UnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""


class Engine(Generic[UnitOfWorkType], abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[UnitOfWorkType]:
        """Build a unit of work."""


class RepositoryError(Exception):
    """An exception raised when loading data from a repository."""
