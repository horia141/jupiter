"""Helpers for working with entities."""
import abc
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional

from models.basic import EntityId, Timestamp

BAD_REF_ID = EntityId("bad-entity-id")


UpdateActionType = TypeVar('UpdateActionType')


class UpdateAction(Generic[UpdateActionType]):
    """The update action for a field."""

    _value: Optional[UpdateActionType]

    def __init__(self, value: Optional[UpdateActionType] = None) -> None:
        """Constructor."""
        self._value = value

    @staticmethod
    def do_nothing() -> 'UpdateAction[UpdateActionType]':
        """An update action where nothing needs to happen."""
        return UpdateAction[UpdateActionType]()

    @staticmethod
    def change_to(value: UpdateActionType) -> 'UpdateAction[UpdateActionType]':
        """An update action where the value needs to be changed to a new value."""
        return UpdateAction[UpdateActionType](value)

    @property
    def should_change(self) -> bool:
        """Whether the value should change or not."""
        return self._value is not None

    @property
    def value(self) -> UpdateActionType:
        """Return the value if it exists."""
        if self._value is None:
            raise Exception("Trying to get the value when it's not there")
        return self._value


@dataclass(frozen=True)
class Event:
    """The base class for all events."""

    timestamp: Timestamp


@dataclass()
class AggregateRoot:
    """The base class for all aggregate roots."""

    @dataclass(frozen=True)
    class Created(Event):
        """Created event."""

    @dataclass(frozen=True)
    class Archived(Event):
        """Archived event."""

    _ref_id: EntityId
    _archived: bool
    _created_time: Timestamp
    _archived_time: Optional[Timestamp]
    _last_modified_time: Timestamp
    _events: List[Event]

    def assign_ref_id(self, ref_id: EntityId) -> None:
        """Assign a ref id to the root."""
        self._ref_id = ref_id

    def mark_archived(self, archived_time: Timestamp) -> None:
        """Archive the root."""
        self._archived = True
        self._archived_time = archived_time
        self.record_event(AggregateRoot.Archived(timestamp=archived_time))

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
    def archived_time(self) -> Optional[Timestamp]:
        """The archived time."""
        return self._archived_time

    @property
    def last_modified_time(self) -> Timestamp:
        """The last modified time."""
        return self._last_modified_time

CommandArgs = TypeVar('CommandArgs')
CommandResult = TypeVar('CommandResult')


class Command(Generic[CommandArgs, CommandResult], abc.ABC):
    """A command."""

    @abc.abstractmethod
    def execute(self, args: CommandArgs) -> CommandResult:
        """Execute the command's action."""
