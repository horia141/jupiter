"""A simpler type of entity."""
import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    TypeAlias,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.concept import Concept
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import IsOneOfRefId, IsRefId, ParentLink
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.value import AtomicValue, EnumValue
from typing_extensions import dataclass_transform

_RecordT = TypeVar("_RecordT", bound="Record")


@dataclass(frozen=True)
class Record(Concept):
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


@dataclass_transform(frozen_default=True)
def record(cls: type[_RecordT]) -> type[_RecordT]:
    """A decorator that marks a class as a record."""
    return dataclass(frozen=True)(cls)


RecordLinkFilterRaw: TypeAlias = None | AtomicValue[Primitive] | EnumValue | IsRefId
RecordLinkFilterCompiled = None | AtomicValue[Primitive] | EnumValue | EntityId
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


def _check_record_can_be_filterd_by(
    cls: type[_RecordT], filters: RecordLinkFiltersRaw
) -> None:
    def _get_real_type(cls: type[_RecordT]) -> tuple[type[_RecordT], bool]:
        base_type = get_origin(cls)
        if base_type is Union:
            base_args = get_args(cls)
            if len(base_args) > 2:
                raise Exception(f"Type {cls} is not compatible with record types")
            if type(None) in base_args:
                return base_args[0], True
            else:
                raise Exception(f"Type {cls} is not compatible with record types")
        else:
            return cls, False

    all_fields = dataclasses.fields(cls)

    for filter_name, filter_rule in filters.items():
        found_field = None
        for field in all_fields:
            if field.name == filter_name:
                found_field = field
                break
            elif field.type is ParentLink and filter_name == field.name + "_ref_id":
                found_field = field
                break
        else:
            raise Exception(f"Record {cls} does not have a field {filter_name}")

        found_field_type, found_field_optional = _get_real_type(found_field.type)

        if found_field_optional:
            if filter_rule is None:
                continue

        if issubclass(found_field_type, AtomicValue):
            if isinstance(filter_rule, AtomicValue):  # type: ignore[unreachable]
                if found_field_type != filter_rule.__class__:
                    raise Exception(
                        f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                    )
            elif isinstance(filter_rule, EnumValue):  # type: ignore[unreachable]
                raise Exception(
                    f"Filter rule for {filter_name} is {filter_rule.__class__} which is not correct"
                )
            elif isinstance(filter_rule, IsRefId) or isinstance(
                filter_rule, IsOneOfRefId
            ):
                if found_field_type != EntityId and found_field_type != ParentLink:
                    raise Exception(
                        f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                    )
            else:
                raise Exception(
                    f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                )
        elif issubclass(found_field_type, EnumValue):
            if isinstance(filter_rule, AtomicValue):  # type: ignore[unreachable]
                raise Exception(
                    f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                )
            elif isinstance(filter_rule, EnumValue):  # type: ignore[unreachable]
                if found_field_type != filter_rule.__class__:
                    raise Exception(
                        f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                    )
            elif isinstance(filter_rule, IsRefId) or isinstance(
                filter_rule, IsOneOfRefId
            ):
                if found_field_type != EntityId and found_field_type != ParentLink:
                    raise Exception(
                        f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                    )
            else:
                raise Exception(
                    f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                )
        elif issubclass(found_field_type, ParentLink):
            if not isinstance(filter_rule, IsRefId):  # type: ignore[unreachable]
                raise Exception(
                    f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not correct"
                )
        else:
            raise Exception(
                f"Filter rule for '{filter_name}' is {filter_rule.__class__} which is not supported"
            )
