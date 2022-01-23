"""Framework level elements for aggregate roots."""
import dataclasses
from dataclasses import dataclass
from typing import Optional, List, TypeVar, Union, cast

from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import Event, EventKind, EventSource

FIRST_VERSION = 0


_AggregateRootType = TypeVar('_AggregateRootType', bound='AggregateRoot')


@dataclass(frozen=True)
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
    version: int = dataclasses.field(compare=False, hash=False)
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp
    archived_time: Optional[Timestamp]
    events: List[Event] = dataclasses.field(compare=False, hash=False)

    def _new_version(
            self: _AggregateRootType, new_event: Event,
            **kwargs: Union[None, bool, str, int, float, object]) -> _AggregateRootType:
        # To hell with your types!
        # We only want to create a new version if there's any actual change in the root. This means we both
        # create a new object, and we increment it's version, and emit a new event. Otherwise we just return
        # the original object.
        for arg_name, arg_value in kwargs.items():
            # TODO(horia141): there's no way this logic can't be better!
            # The first condition is a global one and will result in this returning on the first iteration of the loop
            # even if all the fields are the same.
            # The way remote updates work is that you don't do an update if the remote entity hasn't been modified. To
            # save on a lot of API calls and keep things fast. But, if it has been modified, we still want an update
            # regardless if a change has happened or not in the physical structure of the entity.
            if (new_event.source == EventSource.NOTION and self.last_modified_time < new_event.timestamp) \
                    or arg_value != getattr(self, arg_name):
                new_events = self.events.copy()
                new_events.append(new_event)
                return cast(
                    _AggregateRootType,
                    dataclasses.replace(
                        self,
                        version=new_event.entity_version,
                        last_modified_time=new_event.timestamp,
                        events=new_events,
                        **kwargs))
        return self

    def assign_ref_id(self: _AggregateRootType, ref_id: EntityId) -> _AggregateRootType:
        """Assign a ref id to the root."""
        return dataclasses.replace(self, ref_id=ref_id)

    def mark_archived(self: _AggregateRootType, source: EventSource, archived_time: Timestamp) -> _AggregateRootType:
        """Archive the root."""
        return self._new_version(
            archived=True,
            archived_time=archived_time,
            new_event=AggregateRoot.Archived.make_event_from_frame_args(source, self.version, archived_time))

    def change_archived(
            self: _AggregateRootType, archived: bool, source: EventSource,
            archived_time: Timestamp) -> _AggregateRootType:
        """Change the archival status."""
        if self.archived == archived:
            return self
        if archived:
            return self._new_version(
                archived=True,
                archived_time=archived_time,
                new_event=AggregateRoot.Archived.make_event_from_frame_args(source, self.version, archived_time))
        else:
            return self._new_version(
                archived=False,
                archived_time=None,
                new_event=AggregateRoot.Restore.make_event_from_frame_args(source, self.version, archived_time))
