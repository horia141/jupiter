"""Framework level elements for aggregate roots."""
from dataclasses import dataclass
from typing import Optional, List

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import Event, EventKind


FIRST_VERSION = 1


@dataclass()
class AggregateRoot:
    """The base class for all aggregate roots."""

    @dataclass(frozen=True)
    class Created(Event):
        """Created event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.CREATE

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.UPDATE

    @dataclass(frozen=True)
    class Archived(Event):
        """Archived event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.ARCHIVE

    @dataclass(frozen=True)
    class Restore(Event):
        """Restore event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.RESTORE

    ref_id: EntityId
    version: int
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]
    events: List[Event]

    def assign_ref_id(self, ref_id: EntityId) -> None:
        """Assign a ref id to the root."""
        self.ref_id = ref_id

    def mark_archived(self, archived_time: Timestamp) -> None:
        """Archive the root."""
        self.archived = True
        self.archived_time = archived_time
        self.record_event(AggregateRoot.Archived.make_event_from_frame_args(archived_time))

    def change_archived(self, archived: bool, archived_time: Timestamp) -> None:
        """Change the archival status."""
        if self.archived == archived:
            return
        elif not self.archived and archived:
            self.archived = True
            self.archived_time = archived_time
            self.record_event(AggregateRoot.Archived.make_event_from_frame_args(archived_time))
        elif self.archived and not archived:
            self.archived = False
            self.archived_time = None
            self.record_event(AggregateRoot.Restore.make_event_from_frame_args(archived_time))
        else:
            return

    def record_event(self, event: Event) -> None:
        """Record an event on the root."""
        self.version = self.version + 1
        self.last_modified_time = event.timestamp
        self.events.append(event)
