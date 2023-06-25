"""Framework level elements for entities."""
import abc
import dataclasses
from dataclasses import dataclass
from typing import List, Optional, TypeVar, Union, cast

from jupiter.core.domain.tag_name import TagName
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.event import Event, EventKind, EventSource

FIRST_VERSION = 0


_EntityT = TypeVar("_EntityT", bound="Entity")


@dataclass
class Entity:
    """The base class for all entities."""

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
        self: _EntityT,
        new_event: Event,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _EntityT:
        # To hell with your types!
        # We only want to create a new version if there's any actual change in the root. This means we both
        # create a new object, and we increment it's version, and emit a new event. Otherwise we just return
        # the original object.
        for arg_name, arg_value in kwargs.items():
            if arg_value != getattr(self, arg_name):
                new_events = self.events.copy()
                new_events.append(new_event)
                return cast(
                    _EntityT,
                    dataclasses.replace(
                        self,
                        version=new_event.entity_version,
                        last_modified_time=new_event.timestamp,
                        events=new_events,
                        **kwargs,
                    ),
                )
        return self

    def assign_ref_id(self: _EntityT, ref_id: EntityId) -> _EntityT:
        """Assign a ref id to the root."""
        return dataclasses.replace(self, ref_id=ref_id)

    def mark_archived(
        self: _EntityT,
        source: EventSource,
        archived_time: Timestamp,
    ) -> _EntityT:
        """Archive the root."""
        return self._new_version(
            archived=True,
            archived_time=archived_time,
            new_event=Entity.Archived.make_event_from_frame_args(
                source,
                self.version,
                archived_time,
            ),
        )


@dataclass
class RootEntity(Entity):
    """An entity without any parent."""

    # example: workspace, user


@dataclass
class TrunkEntity(Entity, abc.ABC):
    """An entity with children, which is also a singleton."""

    # examples:  vacations collection, projects collection, smart list collection, integrations collection,
    # Zapier+Mail collection, etc

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this trunk entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@dataclass
class StubEntity(Entity):
    """An entity with no children, but which is also a singleton."""

    # examples: GitHub connection, GSuite connection, etc

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this stub entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@dataclass
class BranchEntity(Entity):
    """An entity with leaf children, which is also a group child of another sort of branch."""

    # examples: smart list, metric, feeds (future)

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this branch entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@dataclass
class LeafEntity(Entity):
    """An entity  with no children, sitting as a child of some other branch entity, at the top of the entity tree."""

    # examples: inbox task, vacation, project, smart list item etc.

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this branch entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@dataclass
class BranchTagEntity(LeafEntity, abc.ABC):
    """A leaf entity serving as a tag for other entities on a branch.."""

    tag_name: TagName
