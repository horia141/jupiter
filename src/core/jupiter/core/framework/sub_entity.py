"""Framework level elements for sub entities (entity in DDD)."""
import dataclasses
from dataclasses import dataclass
from typing import List, Optional, TypeVar, Union, cast

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import Event, EventKind, EventSource

FIRST_VERSION = 0


_SubEntityT = TypeVar("_SubEntityT", bound="SubEntity")


@dataclass
class SubEntity:
    """The base class for all sub entities."""

    @dataclass
    class Created(Event):
        """Created event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.CREATE

    @dataclass
    class Updated(Event):
        """Updated event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.UPDATE

    @dataclass
    class Archived(Event):
        """Archived event."""

        @property
        def kind(self) -> EventKind:
            """The kind of the event."""
            return EventKind.ARCHIVE

    ref_id: EntityId
    version: int = dataclasses.field(compare=False, hash=False)
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp = dataclasses.field(compare=False, hash=False)
    archived_time: Optional[Timestamp]
    events: List[Event] = dataclasses.field(compare=False, hash=False)

    def _new_version(
        self: _SubEntityT,
        new_event: Event,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _SubEntityT:
        # To hell with your types!
        # We only want to create a new version if there's any actual change in the root. This means we both
        # create a new object, and we increment it's version, and emit a new event. Otherwise we just return
        # the original object.
        for arg_name, arg_value in kwargs.items():
            if arg_value != getattr(self, arg_name):
                new_events = self.events.copy()
                new_events.append(new_event)
                return cast(
                    _SubEntityT,
                    dataclasses.replace(
                        self,
                        version=new_event.entity_version,
                        last_modified_time=new_event.timestamp,
                        events=new_events,
                        **kwargs,
                    ),
                )
        return self

    def assign_ref_id(self: _SubEntityT, ref_id: EntityId) -> _SubEntityT:
        """Assign a ref id to the root."""
        return dataclasses.replace(self, ref_id=ref_id)

    def mark_archived(
        self: _SubEntityT,
        source: EventSource,
        archived_time: Timestamp,
    ) -> _SubEntityT:
        """Archive the root."""
        return self._new_version(
            archived=True,
            archived_time=archived_time,
            new_event=SubEntity.Archived.make_event_from_frame_args(
                source,
                self.version,
                archived_time,
            ),
        )
