"""Framework level elements for entities (aggregate roots in DDD)."""
import abc
import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Optional, Type, TypeVar, Union, cast

from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.event import Event, EventKind
from jupiter.core.framework.value import EnumValue, Value
from typing_extensions import dataclass_transform

FIRST_VERSION = 1


_EntityT = TypeVar("_EntityT", bound="Entity")


@dataclass
class Entity:
    """The base class for all entities."""

    ref_id: EntityId
    version: int = dataclasses.field(compare=False, hash=False)
    archived: bool
    created_time: Timestamp
    last_modified_time: Timestamp = dataclasses.field(compare=False, hash=False)
    archived_time: Optional[Timestamp]
    events: List[Event] = dataclasses.field(compare=False, hash=False)

    @classmethod
    def _create(
        cls: Type[_EntityT],
        ctx: DomainContext,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _EntityT:
        """Create a new entity."""
        return cls(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=ctx.action_timestamp,
            last_modified_time=ctx.action_timestamp,
            archived_time=None,
            events=[],
            **kwargs,
        )

    def _new_version(
        self: _EntityT,
        ctx: DomainContext,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _EntityT:
        # To hell with your types!
        # We only want to create a new version if there's any actual change in the root. This means we both
        # create a new object, and we increment it's version, and emit a new event. Otherwise we just return
        # the original object.
        for arg_name, arg_value in kwargs.items():
            if arg_value != getattr(self, arg_name):
                return cast(
                    _EntityT,
                    dataclasses.replace(
                        self,
                        version=self.version + 1,
                        events=self.events.copy(),
                        last_modified_time=ctx.action_timestamp,
                        **kwargs,  # type: ignore[arg-type]
                    ),
                )
        return self

    def assign_ref_id(self: _EntityT, ref_id: EntityId) -> _EntityT:
        """Assign a ref id to the root."""
        return dataclasses.replace(self, ref_id=ref_id)

    def mark_archived(
        self: _EntityT,
        ctx: DomainContext,
    ) -> _EntityT:
        """Archive the root."""
        archived_entity = self._new_version(
            ctx=ctx,
            archived=True,
            archived_time=ctx.action_timestamp,
        )
        archived_entity.events.append(
            Event(
                source=ctx.event_source,
                entity_version=archived_entity.version,
                timestamp=ctx.action_timestamp,
                frame_args={},
                kind=EventKind.ARCHIVE,
                name="mark_archived",
            )
        )
        return archived_entity


@dataclass_transform()
def entity(cls: type[_EntityT]) -> type[_EntityT]:
    return dataclass(cls)


@dataclass
class IsRefId:
    """Transforms a generic filter based on the current entity's ref id."""


@dataclass
class IsOneOfRefId:
    """Transforms a generic filter based on a current entity's field with a list of ref ids."""

    field_name: str

    def __init__(self, field_name: str):
        """Constructor."""
        self.field_name = field_name


EntityLinkFilterRaw = Value | EnumValue | IsRefId | IsOneOfRefId
EntityLinkFilterCompiled = Value | EnumValue | EntityId | list[EntityId]
EntityLinkFiltersRaw = dict[str, EntityLinkFilterRaw]
EntityLinkFiltersCompiled = dict[str, EntityLinkFilterCompiled]


@dataclass(init=False)
class EntityLink(Generic[_EntityT]):
    """An entity link descriptor."""

    the_type: Type[_EntityT]
    filters: EntityLinkFiltersRaw

    def __init__(self, the_type: Type[_EntityT], **kwargs: EntityLinkFilterRaw):
        """Constructor."""
        self.the_type = the_type
        self.filters = kwargs

    def get_for_entity(self, entity: Entity) -> EntityLinkFiltersCompiled:
        """Get the filters for an entity."""
        reified_filters: EntityLinkFiltersCompiled = {}
        for k, v in self.filters.items():
            if isinstance(v, Value):
                reified_filters[k] = v
            elif isinstance(v, EnumValue):
                reified_filters[k] = v
            elif isinstance(v, IsRefId):
                reified_filters[k] = entity.ref_id
            else:
                possible = getattr(entity, v.field_name)
                if not isinstance(possible, list):
                    raise Exception("Invalid type of filter")
                if len(possible) == 0:
                    continue
                    # raise Exception("Invalid type of filter")
                if not isinstance(possible[0], EntityId):
                    raise Exception("Invalid type of filter")
                reified_filters[k] = possible
        return reified_filters


class ContainsLink(Generic[_EntityT], EntityLink[_EntityT]):
    """An entity that contains another entity."""


class ContainsOne(Generic[_EntityT], ContainsLink[_EntityT]):
    """An entity that can contain exactly one other entity."""


class ContainsAtMostOne(Generic[_EntityT], ContainsLink[_EntityT]):
    """An entity that can contain at most one other entity."""


class ContainsMany(Generic[_EntityT], ContainsLink[_EntityT]):
    """An entity that can contain many other entities."""


class OwnsLink(Generic[_EntityT], EntityLink[_EntityT]):
    """An entity that owns another entity."""


class OwnsOne(Generic[_EntityT], OwnsLink[_EntityT]):
    """An entity that can owns exactly one other entity."""


class OwnsAtMostOne(Generic[_EntityT], OwnsLink[_EntityT]):
    """An entity that can only be owned by at most one other entity."""


class OwnsMany(Generic[_EntityT], OwnsLink[_EntityT]):
    """An entity that can only be owned by at most one other entity."""


class RefsLink(Generic[_EntityT], EntityLink[_EntityT]):
    """An entity that references another entity."""


class RefsOne(Generic[_EntityT], RefsLink[_EntityT]):
    """An entity that can reference exactly one other entity."""


class RefsAtMostOne(Generic[_EntityT], RefsLink[_EntityT]):
    """An entity that can reference at most one other entity."""


class RefsMany(Generic[_EntityT], RefsLink[_EntityT]):
    """An entity that can reference many other entities."""


def _make_event_from_frame_args(  # type: ignore
    f: Callable[..., Entity],
    ctx: DomainContext,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    event_kind: EventKind,
    entity_version: int,
    created_time: Timestamp,
) -> Event:
    """Construct the data for an event from the arguments of the method which calls this one."""
    arg_names = f.__code__.co_varnames

    # Following logic is convoluted to avoid allocations.
    # Presume args are either ctx, a, b, ... or self, ctx, a, b, ...

    frame_args = {}
    to_skip = 0
    for arg_name in arg_names:
        if arg_name == "self" or arg_name == "ctx":
            # This is called from some sort of method of an entity class and we're looking
            # at this frame. There is a self and it's the entity itself! Ditto don't need to
            # map the source again. Nor the special `event_type'.
            to_skip = to_skip + 1
            continue

        arg_index = arg_names.index(arg_name) - to_skip
        if arg_index < len(args):
            arg_value = args[arg_index]
        elif arg_name in kwargs:
            arg_value = kwargs[arg_name]
        else:
            # Local variable, free to ignore
            continue

        frame_args[arg_name] = arg_value

    new_event = Event(
        source=ctx.event_source,
        entity_version=entity_version,
        timestamp=created_time,
        frame_args=frame_args,
        kind=event_kind,
        name=f.__name__,
    )
    return new_event


_CreateEventT = TypeVar("_CreateEventT", bound=Callable[..., Entity])  #  type: ignore


def create_entity_action(f: _CreateEventT) -> _CreateEventT:  # type: ignore
    """A decorator that marks an entity method as a creation one."""

    def wrapper(  #  type: ignore
        ctx: DomainContext, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> Entity:
        """The wrapper."""
        new_entity = f(ctx, *args, **kwargs)
        new_entity.events.append(
            _make_event_from_frame_args(
                f,
                ctx,
                args,
                kwargs,
                EventKind.CREATE,
                new_entity.version,
                new_entity.created_time,
            )
        )
        return new_entity

    return cast(_CreateEventT, wrapper)  # type: ignore


_UpdateEventT = TypeVar("_UpdateEventT", bound=Callable[..., Entity])  #  type: ignore


def update_entity_action(f: _UpdateEventT) -> _UpdateEventT:  # type: ignore
    """A decorator that marks an entity method as an update one."""

    def wrapper(self: Entity, ctx: DomainContext, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Entity:  # type: ignore
        """The wrapper."""
        new_entity = f(self, ctx, *args, **kwargs)
        new_entity.events.append(
            _make_event_from_frame_args(
                f,
                ctx,
                args,
                kwargs,
                EventKind.UPDATE,
                new_entity.version,
                new_entity.last_modified_time,
            )
        )
        return new_entity

    return cast(_UpdateEventT, wrapper)  # type: ignore


@entity
class RootEntity(Entity):
    """An entity without any parent."""

    # example: workspace, user


@entity
class TrunkEntity(Entity, abc.ABC):
    """An entity with children, which is also a singleton."""

    # examples:  vacations collection, projects collection, smart list collection, integrations collection,
    # Zapier+Mail collection, etc

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this trunk entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@entity
class StubEntity(Entity):
    """An entity with no children, but which is also a singleton."""

    # examples: GitHub connection, GSuite connection, etc

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this stub entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@entity
class CrownEntity(Entity):
    """A common name for branch and leaf entities."""

    name: EntityName

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent of this branch entity."""
        raise NotImplementedError("""Needs to be implemented.""")


@dataclass
class BranchEntity(CrownEntity):
    """An entity with leaf children, which is also a group child of another sort of branch."""

    # examples: smart list, metric, feeds (future)


@dataclass
class LeafEntity(CrownEntity):
    """An entity  with no children, sitting as a child of some other branch entity, at the top of the entity tree."""

    # examples: inbox task, vacation, project, smart list item etc.


@dataclass
class BranchTagEntity(LeafEntity, abc.ABC):
    """A leaf entity serving as a tag for other entities on a branch.."""

    tag_name: TagName
