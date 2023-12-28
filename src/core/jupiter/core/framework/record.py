"""A simpler type of entity."""
import dataclasses
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union, cast

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import IsRefId
from jupiter.core.framework.value import EnumValue, Value
from typing_extensions import dataclass_transform

_RecordT = TypeVar("_RecordT", bound="Record")


@dataclass
class Record:
    """A base class for a simplified object to store."""

    created_time: Timestamp
    last_modified_time: Timestamp

    @classmethod
    def _create(
        cls: type[_RecordT],
        ctx: DomainContext,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _RecordT:
        """Create a new record."""
        return cls(
            created_time=ctx.action_timestamp,
            last_modified_time=ctx.action_timestamp,
            **kwargs,
        )

    def _new_version(
        self: _RecordT,
        ctx: DomainContext,
        **kwargs: Union[None, bool, str, int, float, object],
    ) -> _RecordT:
        # To hell with your types!
        # We only want to create a new version if there's any actual change in the root. This means we both
        # create a new object, and we increment it's version, and emit a new event. Otherwise we just return
        # the original object.
        for arg_name, arg_value in kwargs.items():
            if arg_value != getattr(self, arg_name):
                return cast(
                    _RecordT,
                    dataclasses.replace(
                        self,
                        last_modified_time=ctx.action_timestamp,
                        **kwargs,  # type: ignore[arg-type]
                    ),
                )
        return self


@dataclass_transform()
def record(cls: type[_RecordT]) -> type[_RecordT]:
    return dataclass(cls)


RecordLinkFilterRaw = Value | EnumValue | IsRefId
RecordLinkFilterCompiled = Value | EnumValue | EntityId
RecordLinkFiltersRaw = dict[str, RecordLinkFilterRaw]
RecordLinkFiltersCompiled = dict[str, RecordLinkFilterCompiled]


@dataclass(init=False)
class RecordLink(Generic[_RecordT]):
    """A record link descriptor."""

    the_type: type[_RecordT]
    filters: RecordLinkFiltersRaw

    def __init__(self, the_type: type[_RecordT], **kwargs: RecordLinkFilterRaw):
        """Constructor."""
        self.the_type = the_type
        self.filters = kwargs


class ContainsRecords(Generic[_RecordT], RecordLink[_RecordT]):
    """A record link descriptor that contains records."""


_CreateEventT = TypeVar("_CreateEventT", bound=Callable[..., Record])  #  type: ignore


def create_record_action(f: _CreateEventT) -> _CreateEventT:  # type: ignore
    """A decorator that marks a record method as a creation one."""

    def wrapper(  #  type: ignore
        ctx: DomainContext, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> Record:
        """The wrapper."""
        return f(ctx, *args, **kwargs)

    return cast(_CreateEventT, wrapper)  # type: ignore


_UpdateEventT = TypeVar("_UpdateEventT", bound=Callable[..., Record])  #  type: ignore


def update_record_action(f: _UpdateEventT) -> _UpdateEventT:  # type: ignore
    """A decorator that marks a record method as an update one."""

    def wrapper(self: Record, ctx: DomainContext, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Record:  # type: ignore
        """The wrapper."""
        return f(self, ctx, *args, **kwargs)

    return cast(_UpdateEventT, wrapper)  # type: ignore
