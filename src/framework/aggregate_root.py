"""Framework level elements for aggregate roots."""
from dataclasses import dataclass
from typing import Optional, List, Iterable

from domain.timestamp import Timestamp
from framework.entity_id import EntityId
from framework.event import Event


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
