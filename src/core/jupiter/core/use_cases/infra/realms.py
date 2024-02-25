"""Application-specific realm helpers."""
import abc
import dataclasses
import types
import typing
from collections.abc import Mapping
from datetime import date, datetime
from types import GenericAlias, ModuleType
from typing import (
    Final,
    ForwardRef,
    Generic,
    Iterator,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

from jupiter.core.framework.base.entity_id import (
    EntityId,
    EntityIdDatabaseDecoder,
    EntityIdDatabaseEncoder,
    EntityIdWebEncoder,
)
from jupiter.core.framework.base.entity_name import (
    NOT_USED_NAME,
    EntityName,
    EntityNameDatabaseDecoder,
    EntityNameDatabaseEncoder,
)
from jupiter.core.framework.base.timestamp import (
    Timestamp,
    TimestampDatabaseDecoder,
    TimestampDatabaseEncoder,
)
from jupiter.core.framework.concept import Concept
from jupiter.core.framework.entity import Entity, ParentLink
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    PROVIDE_VIA_REGISTRY,
    CliRealm,
    DatabaseRealm,
    DomainThing,
    EventStoreRealm,
    Realm,
    RealmCodecRegistry,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
    WebRealm,
    allowed_in_realm,
)
from jupiter.core.framework.record import Record
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.utils import (
    find_all_modules,
    is_thing_ish_type,
    normalize_optional,
)
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
)
from pendulum.date import Date
from pendulum.datetime import DateTime

_RealmT = TypeVar("_RealmT", bound=Realm)
_DomainThingT = TypeVar("_DomainThingT", bound=DomainThing)
_PrimitiveT = TypeVar("_PrimitiveT", bound=Primitive)
_AtomicValueT = TypeVar("_AtomicValueT", bound=AtomicValue[Primitive])
_CompositeValueT = TypeVar("_CompositeValueT", bound=CompositeValue)
_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)
_EntityT = TypeVar("_EntityT", bound=Entity)
_RecordT = TypeVar("_RecordT", bound=Record)
_UseCaseArgsT = TypeVar("_UseCaseArgsT", bound=UseCaseArgsBase)
_UseCaseResultT = TypeVar("_UseCaseResultT", bound=UseCaseResultBase)


# What can we handle with the things here, let's take a look!
#
# A Thing is:
#     Literal[str]
#     ValueIsh = Primitive | Value
#       where Value = AtomicValue | CompositeValue | EnumValue | SecretValue
#     ComplexIsh = Entity | Record
#
# A CompositeValue is a collection of fields, each of which can be:
#     ValueFieldType:
#       Literal[str]
#       Primitive
#       Value
#       list[ValueFieldType]
#       dict[Primitive | AtomicValue | EnumValue, ValueFieldType]
#       union[*ValueFieldType]
#
# An Entity is a collection of fields, each of which can be:
#     ValueFieldType
#     ParentLink
#     EntityLink
# A Record is a collection of fields, each of which can be:
#     ValueFieldType
#     ParentLink
#     EntityLink


class _LiteralEncoder(Generic[_RealmT], RealmEncoder[str, _RealmT]):

    _allowed_values: list[str]
    _realm: type[_RealmT]

    def __init__(self, allowed_values: list[str], realm: type[_RealmT]) -> None:
        self._allowed_values = allowed_values
        self._realm = realm

    def encode(self, value: str) -> RealmThing:
        if value not in self._allowed_values:
            raise Exception(f"Expected value to be one of {self._allowed_values}")
        return value


class _LiteralDecoder(Generic[_RealmT], RealmDecoder[str, _RealmT]):

    _allowed_values: list[str]
    _realm: type[_RealmT]

    def __init__(self, allowed_values: list[str], realm: type[_RealmT]) -> None:
        self._allowed_values = allowed_values
        self._realm = realm

    def decode(self, value: RealmThing) -> str:
        if not isinstance(value, str) or value not in self._allowed_values:
            raise RealmDecodingError(
                f"Expected value to be one of {self._allowed_values}"
            )
        return value


class _UpdateActionEventStoreEncoder(
    RealmEncoder[UpdateAction[DomainThing], EventStoreRealm]
):
    """An encoder for update actions in the event store realm."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: Final[type[Realm]]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[Realm],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: UpdateAction[DomainThing]) -> RealmThing:
        if not value.should_change:
            return {"should_change": False}

        encoder = self._realm_codec_registry.get_encoder(
            self._the_type, self._realm, self._root_type
        )

        return {
            "should_change": True,
            "value": encoder.encode(value.just_the_value),
        }


class _UpdateActionWebDecoder(RealmDecoder[UpdateAction[DomainThing], WebRealm]):
    """An decoder for update actions in web realm."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: Final[type[Realm]]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[Realm],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> UpdateAction[DomainThing]:
        if not isinstance(value, dict):
            raise RealmDecodingError(
                f"Expected value of type update action for {self._the_type}"
            )

        if "should_change" not in value:
            raise RealmDecodingError(
                f"Expected field to have a should_change field for {self._the_type}"
            )

        final_value: UpdateAction[DomainThing]

        if value["should_change"] is False:
            final_value = UpdateAction.do_nothing()
        else:

            if isinstance(self._the_type, ForwardRef) or isinstance(
                self._the_type, str
            ):
                raise Exception("Off the beaten codepath")

            field_type, is_optional = normalize_optional(self._the_type)
            if "value" not in value:
                if is_optional:
                    final_value = UpdateAction.change_to(None)
                else:
                    raise RealmDecodingError(
                        f"Expected field to have a value field for {self._the_type}"
                    )
            else:
                update_action_decoder = self._realm_codec_registry.get_decoder(
                    field_type, self._realm, self._root_type
                )

                final_value = UpdateAction.change_to(
                    update_action_decoder.decode(value["value"])
                )

        return final_value


class _UnionEncoder(Generic[_RealmT], RealmEncoder[DomainThing, _RealmT]):
    """An encoder for unions."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_types: list[type[DomainThing] | ForwardRef | str]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_types: list[type[DomainThing] | ForwardRef | str],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_types = the_types
        self._realm = realm

    def encode(self, value: DomainThing) -> RealmThing:
        """Encode a realm to a string."""
        for attempt_type in self._the_types:
            try:
                encoder = self._realm_codec_registry.get_encoder(
                    attempt_type, self._realm, self._root_type
                )
                return encoder.encode(value)
            except (RealmDecodingError, Exception):
                pass

        raise RealmDecodingError(
            f"Could not encode value {value} of type {value.__class__.__name__}"
        )


class _UnionDecoder(Generic[_RealmT], RealmDecoder[DomainThing, _RealmT]):
    """An ecnoder for unions."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_types: list[type[DomainThing] | ForwardRef | str]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_types: list[type[DomainThing] | ForwardRef | str],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_types = the_types
        self._realm = realm

    def decode(self, value: RealmThing) -> DomainThing:
        """Decode a realm from a string."""
        for attempt_type in self._the_types:
            try:
                return self._realm_codec_registry.get_decoder(
                    attempt_type, self._realm, self._root_type
                ).decode(value)
            except (InputValidationError, RealmDecodingError):
                pass

        raise RealmDecodingError(
            f"Could not decode value {value} of type {value.__class__.__name__}"
        )


class _ListEncoder(Generic[_RealmT], RealmEncoder[list[DomainThing], _RealmT]):
    """An encoder for lists."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: list[DomainThing]) -> RealmThing:
        """Encode a realm to a string."""
        encoder = self._realm_codec_registry.get_encoder(
            self._the_type, self._realm, self._root_type
        )
        return [encoder.encode(v) for v in value]


class _ListDecoder(Generic[_RealmT], RealmDecoder[list[DomainThing], _RealmT]):
    """An encoder for lists."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> list[DomainThing]:
        """Decode a realm from a string."""
        if not isinstance(value, list):
            raise RealmDecodingError(
                f"Expected value for {value.__class__.__name__} to be a list"
            )
        decoder = self._realm_codec_registry.get_decoder(
            self._the_type, self._realm, self._root_type
        )
        return [decoder.decode(v) for v in value]


class _SetEncoder(Generic[_RealmT], RealmEncoder[set[DomainThing], _RealmT]):
    """An encoder for sets."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: set[DomainThing]) -> RealmThing:
        """Encode a realm to a string."""
        encoder = self._realm_codec_registry.get_encoder(
            self._the_type, self._realm, self._root_type
        )
        return [encoder.encode(v) for v in value]


class _SetDecoder(Generic[_RealmT], RealmDecoder[set[DomainThing], _RealmT]):
    """An encoder for sets."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> set[DomainThing]:
        """Decode a realm from a string."""
        if not isinstance(value, list):
            raise RealmDecodingError(
                f"Expected value for {value.__class__.__name__} to be a list"
            )
        decoder = self._realm_codec_registry.get_decoder(
            self._the_type, self._realm, self._root_type
        )
        return {decoder.decode(v) for v in value}


class _DictEncoder(
    Generic[_RealmT], RealmEncoder[dict[DomainThing, DomainThing], _RealmT]
):
    """An encoder for dicts."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_key_type: type[DomainThing] | ForwardRef | str
    _the_value_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_key_type: type[DomainThing] | ForwardRef | str,
        the_value_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_key_type = the_key_type
        self._the_value_type = the_value_type
        self._realm = realm

    def encode(self, value: dict[DomainThing, DomainThing]) -> RealmThing:
        """Encode a realm to a string."""
        key_encoder = self._realm_codec_registry.get_encoder(
            self._the_key_type, self._realm, self._root_type
        )
        value_encoder = self._realm_codec_registry.get_encoder(
            self._the_value_type, self._realm, self._root_type
        )
        result = {}
        for k, v in value.items():
            encoded_key = key_encoder.encode(k)
            if not isinstance(encoded_key, str):
                raise RealmDecodingError(
                    f"Expected encoded key for {k} to be a string, got {encoded_key}"
                )
            result[encoded_key] = value_encoder.encode(v)
        return result


class _DictDecoder(
    Generic[_RealmT], RealmDecoder[dict[DomainThing, DomainThing], _RealmT]
):
    """An encoder for dicts."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _root_type: type[DomainThing] | None
    _the_key_type: type[DomainThing] | ForwardRef | str
    _the_value_type: type[DomainThing] | ForwardRef | str
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        root_type: type[DomainThing] | None,
        the_key_type: type[DomainThing] | ForwardRef | str,
        the_value_type: type[DomainThing] | ForwardRef | str,
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._root_type = root_type
        self._the_key_type = the_key_type
        self._the_value_type = the_value_type
        self._realm = realm

    def decode(self, value: RealmThing) -> dict[DomainThing, DomainThing]:
        """Decode a realm from a string."""
        if not isinstance(value, dict):
            raise RealmDecodingError(
                f"Expected value of {value.__class__.__name__} to be a dict object"
            )
        key_decoder = self._realm_codec_registry.get_decoder(
            self._the_key_type, self._realm, self._root_type
        )
        value_decoder = self._realm_codec_registry.get_decoder(
            self._the_value_type, self._realm, self._root_type
        )
        return {
            key_decoder.decode(k): value_decoder.decode(v) for k, v in value.items()
        }


class _StandardPrimitiveDatabaseEncoder(
    Generic[_PrimitiveT], RealmEncoder[_PrimitiveT, DatabaseRealm]
):
    """An encoder for primitive values."""

    _the_type: type[_PrimitiveT]

    def __init__(self, the_type: type[_PrimitiveT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _PrimitiveT) -> RealmThing:
        """Encode a realm to a string."""
        return value


class _StandardPrimitiveDatabaseDecoder(
    Generic[_PrimitiveT], RealmDecoder[_PrimitiveT, DatabaseRealm]
):
    """A decoder for primitive values."""

    _the_type: type[_PrimitiveT]

    def __init__(self, the_type: type[_PrimitiveT]) -> None:
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _PrimitiveT:
        """Decode a realm from a string."""
        if not isinstance(
            value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)
        ):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} in {self.__class__} to be primitive"
            )

        return cast(_PrimitiveT, value)


class PrimitiveAtomicValueDatabaseEncoder(
    Generic[_AtomicValueT], RealmEncoder[_AtomicValueT, DatabaseRealm], abc.ABC
):
    """An encoder for atomic values."""

    def encode(self, value: _AtomicValueT) -> RealmThing:
        """Encode a realm to a string."""
        return self.to_primitive(value)

    @abc.abstractmethod
    def to_primitive(self, value: _AtomicValueT) -> Primitive:
        """Return a primitive form of this atomic value."""


class PrimitiveAtomicValueDatabaseDecoder(
    Generic[_AtomicValueT],
    RealmDecoder[_AtomicValueT, DatabaseRealm],
):
    """An encoder for atomic values."""

    _atomic_value_type: type[_AtomicValueT]

    def __init__(self) -> None:
        self._atomic_value_type = cast(type[_AtomicValueT], get_args(self.__class__.__orig_bases__[0])[0])  # type: ignore[attr-defined]

    def decode(self, value: RealmThing) -> _AtomicValueT:
        """Decode a realm from a string."""
        base_type_hack = self._atomic_value_type.base_type_hack()
        if not isinstance(value, base_type_hack):

            raise RealmDecodingError(
                f"Expected value for in {self.__class__} to be a primitive of type {base_type_hack}"
            )

        if base_type_hack is bool and isinstance(value, bool):
            return self.from_raw_bool(value)
        elif base_type_hack is int and isinstance(value, int):
            return self.from_raw_int(value)
        elif base_type_hack is float and isinstance(value, float):
            return self.from_raw_float(value)
        elif base_type_hack is str and isinstance(value, str):
            return self.from_raw_str(value)
        elif base_type_hack is DateTime and isinstance(value, (datetime, DateTime)):
            return self.from_raw_datetime(value)
        elif base_type_hack is Date and isinstance(value, (date, Date)):
            return self.from_raw_date(value)
        else:
            raise Exception("Off the beaten codepath")

    def from_raw_bool(self, primitive: bool) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")

    def from_raw_int(self, primitive: int) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")

    def from_raw_float(self, primitive: float) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")

    def from_raw_str(self, primitive: str) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")

    def from_raw_date(self, primitive: date | Date) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")

    def from_raw_datetime(self, primitive: datetime | DateTime) -> _AtomicValueT:
        """Transform a primitive form of this atomic value."""
        raise Exception("Off the beaten codepath")


class _StandardCompositeValueEncoder(
    Generic[_CompositeValueT, _RealmT], RealmEncoder[_CompositeValueT, _RealmT]
):
    """An encoder for composite values."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_CompositeValueT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_CompositeValueT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: _CompositeValueT) -> RealmThing:
        """Encode a realm to a string."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(self._the_type)
        for field in all_fields:
            encoder = self._realm_codec_registry.get_encoder(
                field.type, self._realm, self._the_type
            )
            field_value = getattr(value, field.name)
            result[field.name] = encoder.encode(field_value)
        return result


class _StandardCompositeValueDecoder(
    Generic[_CompositeValueT, _RealmT], RealmDecoder[_CompositeValueT, _RealmT]
):
    """A decoder for composite values."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_CompositeValueT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_CompositeValueT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> _CompositeValueT:
        if not isinstance(value, dict):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be a dict object"
            )

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, DomainThing] = {}

        for field in all_fields:
            if field.name not in value:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            decoder = self._realm_codec_registry.get_decoder(
                field.type, self._realm, self._the_type
            )
            field_value = value[field.name]
            ctor_args[field.name] = decoder.decode(field_value)

        return self._the_type(**ctor_args)


class _StandardEnumValueDatabaseEncoder(
    Generic[_EnumValueT], RealmEncoder[_EnumValueT, DatabaseRealm]
):

    _the_type: type[_EnumValueT]

    def __init__(self, the_type: type[_EnumValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _EnumValueT) -> RealmThing:
        """Encode a realm to a string."""
        return str(value.value)


class _StandardEnumValueDatabaseDecoder(
    Generic[_EnumValueT], RealmDecoder[_EnumValueT, DatabaseRealm]
):
    """A codec for enums."""

    _the_type: type[_EnumValueT]

    def __init__(self, the_type: type[_EnumValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _EnumValueT:
        """Decode a realm from a string."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be string"
            )

        value_clean: str = value.strip()

        try:
            return cast(_EnumValueT, self._the_type(value_clean))
        except ValueError:
            raise RealmDecodingError(
                f"Expected enum {self._the_type.__name__} '{value}' to be one of '{','.join(str(s.value) for s in self._the_type)}'",
            ) from None


class _StandardEntityEncoder(
    Generic[_EntityT, _RealmT], RealmEncoder[_EntityT, _RealmT]
):
    """An encoder for entities."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_EntityT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_EntityT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: _EntityT) -> RealmThing:
        """Encode an entity."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(value.__class__)

        for field in all_fields:
            field_value = getattr(value, field.name)
            if field.name == "events":
                continue

            if isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            else:
                encoder = self._realm_codec_registry.get_encoder(
                    field.type, self._realm, self._the_type
                )

                result[field.name] = encoder.encode(field_value)

        return result


class _StandardEntityDecoder(
    Generic[_EntityT, _RealmT], RealmDecoder[_EntityT, _RealmT]
):
    """A decoder for entities."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_EntityT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_EntityT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> _EntityT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, DomainThing | ParentLink] = {}

        entity_id_decoder = self._realm_codec_registry.get_decoder(
            EntityId, self._realm
        )
        timestamp_decoder = self._realm_codec_registry.get_decoder(
            Timestamp, self._realm
        )

        if "ref_id" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a ref_id"
            )
        ref_id = entity_id_decoder.decode(value["ref_id"])
        if "version" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a version"
            )
        if type(value["version"]) is not int:
            raise RealmDecodingError(
                f"Expected version field of type {self._the_type.__name__} to be an integer"
            )
        version = value["version"]
        if "archived" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a archived bit"
            )
        if type(value["archived"]) is not bool:
            raise RealmDecodingError(
                f"Expected archived field of type {self._the_type.__name__} to be a boolean"
            )
        archived = value["archived"]
        if "created_time" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a created time"
            )
        created_time = timestamp_decoder.decode(value["created_time"])
        if "last_modified_time" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a last modified time"
            )
        last_modified_time = timestamp_decoder.decode(value["last_modified_time"])
        if "archived_time" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have an archived time"
            )
        archived_time = (
            timestamp_decoder.decode(value["archived_time"])
            if value["archived_time"] is not None
            else None
        )

        for field in all_fields:
            if field.name in (
                "ref_id",
                "version",
                "archived",
                "created_time",
                "last_modified_time",
                "archived_time",
                "events",
            ):
                continue

            if field.name == "name" and ("name" not in value or value["name"] is None):
                ctor_args[field.name] = NOT_USED_NAME
                continue

            if field.name in value:
                field_value = value[field.name]
            elif field.type is ParentLink and field.name + "_ref_id" in value:
                field_value = value[field.name + "_ref_id"]
            else:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            if field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            else:
                decoder = self._realm_codec_registry.get_decoder(
                    field.type, self._realm, self._the_type
                )
                ctor_args[field.name] = decoder.decode(field_value)

        return self._the_type(
            ref_id=ref_id,
            version=version,
            archived=archived,
            created_time=created_time,
            last_modified_time=last_modified_time,
            archived_time=archived_time,
            events=[],
            **ctor_args,
        )


class _StandardRecordEncoder(
    Generic[_RecordT, _RealmT], RealmEncoder[_RecordT, _RealmT]
):
    """An encoder for records."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_RecordT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_RecordT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def encode(self, value: _RecordT) -> RealmThing:
        """Encode a record."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(value)
        for field in all_fields:
            field_value = getattr(value, field.name)

            if isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            else:
                encoder = self._realm_codec_registry.get_encoder(
                    field.type, self._realm, self._the_type
                )
                result[field.name] = encoder.encode(field_value)

        return result


class _StandardRecordDecoder(
    Generic[_RecordT, _RealmT], RealmDecoder[_RecordT, _RealmT]
):
    """A decoder for records."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_RecordT]
    _realm: type[_RealmT]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        the_type: type[_RecordT],
        realm: type[_RealmT],
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type
        self._realm = realm

    def decode(self, value: RealmThing) -> _RecordT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, DomainThing | ParentLink] = {}

        entity_id_decoder = self._realm_codec_registry.get_decoder(
            EntityId, self._realm
        )
        timestamp_decoder = self._realm_codec_registry.get_decoder(
            Timestamp, self._realm
        )

        if "created_time" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a created time"
            )
        created_time = timestamp_decoder.decode(value["created_time"])
        if "last_modified_time" not in value:
            raise RealmDecodingError(
                f"Expected value of type {self._the_type.__name__} to have a last modified time"
            )
        last_modified_time = timestamp_decoder.decode(value["last_modified_time"])

        for field in all_fields:
            if field.name in (
                "created_time",
                "last_modified_time",
            ):
                continue

            if field.name in value:
                field_value = value[field.name]
            elif field.type is ParentLink and field.name + "_ref_id" in value:
                field_value = value[field.name + "_ref_id"]
            else:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            if field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            else:
                decoder = self._realm_codec_registry.get_decoder(
                    field.type, self._realm, self._the_type
                )
                ctor_args[field.name] = decoder.decode(field_value)

        return self._the_type(
            created_time=created_time,
            last_modified_time=last_modified_time,
            **ctor_args,
        )


class _StandardUseCaseArgsEventStoreEncoder(
    Generic[_UseCaseArgsT], RealmEncoder[_UseCaseArgsT, EventStoreRealm]
):
    """An encoder for use case args."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_UseCaseArgsT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_UseCaseArgsT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def encode(self, value: _UseCaseArgsT) -> RealmThing:
        """Encode a realm to a string."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(self._the_type)
        for field in all_fields:
            encoder = self._realm_codec_registry.get_encoder(
                field.type, EventStoreRealm, self._the_type
            )
            field_value = getattr(value, field.name)
            result[field.name] = encoder.encode(field_value)
        return result


class _StandardUseCaseArgsCliDecoder(
    Generic[_UseCaseArgsT], RealmDecoder[_UseCaseArgsT, CliRealm]
):
    """A decoder for use case args."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_UseCaseArgsT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_UseCaseArgsT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _UseCaseArgsT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, DomainThing | UpdateAction[DomainThing]] = {}

        for field in all_fields:
            if field.name not in value:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            field_value = value[field.name]

            if (
                field_type_origin := get_origin(field.type)
            ) is not None and field_type_origin is UpdateAction:
                update_action_type = cast(type[DomainThing], get_args(field.type)[0])

                final_value: UpdateAction[DomainThing]
                if (
                    f"clear_{field.name}" in value
                    and value[f"clear_{field.name}"] is True
                ):
                    final_value = UpdateAction.change_to(None)
                elif field_value is None:
                    final_value = UpdateAction.do_nothing()
                else:
                    update_action_decoder = self._realm_codec_registry.get_decoder(
                        update_action_type, CliRealm
                    )

                    final_value = UpdateAction.change_to(
                        update_action_decoder.decode(field_value)
                    )

                ctor_args[field.name] = final_value
            else:
                decoder = self._realm_codec_registry.get_decoder(
                    field.type, CliRealm, self._the_type
                )
                ctor_args[field.name] = decoder.decode(field_value)

        return self._the_type(**ctor_args)


class _StandardUseCaseArgsWebDecoder(
    Generic[_UseCaseArgsT], RealmDecoder[_UseCaseArgsT, WebRealm]
):
    """A decoder for use case args."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_UseCaseArgsT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_UseCaseArgsT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _UseCaseArgsT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, DomainThing | UpdateAction[DomainThing]] = {}

        for field in all_fields:
            field_type, is_optional = normalize_optional(field.type)
            if field.name not in value:
                if is_optional:
                    ctor_args[field.name] = None
                else:
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                    )
            else:
                field_value = value[field.name]
                decoder = self._realm_codec_registry.get_decoder(
                    field_type, WebRealm, self._the_type
                )
                ctor_args[field.name] = decoder.decode(field_value)

        return self._the_type(**ctor_args)


class _StandardUseCaseResultWebEncoder(
    Generic[_UseCaseResultT], RealmEncoder[_UseCaseResultT, WebRealm]
):
    """An encoder for use case args."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_UseCaseResultT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_UseCaseResultT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def encode(self, value: _UseCaseResultT) -> RealmThing:
        """Encode a realm to a string."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(self._the_type)
        for field in all_fields:
            encoder = self._realm_codec_registry.get_encoder(
                field.type, WebRealm, self._the_type
            )
            field_value = getattr(value, field.name)
            result[field.name] = encoder.encode(field_value)
        return result


class ModuleExplorerRealmCodecRegistry(RealmCodecRegistry):
    """A registry for realm codecs constructed by exploring a module tree."""

    _encoders_registry: Final[
        dict[tuple[type[Thing], type[Realm]], RealmEncoder[Thing, Realm]]
    ]
    _decoders_registry: Final[
        dict[tuple[type[Thing], type[Realm]], RealmDecoder[Thing, Realm]]
    ]

    def __init__(
        self,
    ) -> None:
        """Initialize the registry."""
        self._encoders_registry = {}
        self._decoders_registry = {}

    @staticmethod
    def build_from_module_root(
        *module_roots: ModuleType,
    ) -> "ModuleExplorerRealmCodecRegistry":
        """Build a registry from a module root using magick."""

        def extract_atomic_values(
            the_module: ModuleType,
        ) -> Iterator[type[AtomicValue[Primitive]]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, AtomicValue)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_composite_values(
            the_module: ModuleType,
        ) -> Iterator[type[CompositeValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, CompositeValue)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_enum_values(
            the_module: ModuleType,
        ) -> Iterator[type[EnumValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, EnumValue)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_entities(
            the_module: ModuleType,
        ) -> Iterator[type[Entity]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Entity)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_records(
            the_module: ModuleType,
        ) -> Iterator[type[Record]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Record)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_use_case_args(
            the_module: ModuleType,
        ) -> Iterator[type[UseCaseArgsBase]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, UseCaseArgsBase)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def extract_use_case_result(
            the_module: ModuleType,
        ) -> Iterator[type[UseCaseResultBase]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, UseCaseResultBase)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        def figure_out_realm(the_type: type) -> type[Realm] | None:
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Realm):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_realm(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def figure_out_concept(the_type: type) -> type[Concept] | None:
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Concept):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_concept(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def extract_concept_encoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmEncoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmEncoder)):
                    continue

                if obj.__module__ == ModuleExplorerRealmCodecRegistry.__module__:
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                concept_type = figure_out_concept(cast(type, obj))
                if concept_type is None:
                    raise Exception(
                        f"Could not infer concept class from encoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )
                realm_type = figure_out_realm(cast(type, obj))
                if realm_type is None:
                    raise Exception(
                        f"Could not infer realm class from encoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )

                yield concept_type, realm_type, cast(type, obj)

        def extract_concept_decoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmDecoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmDecoder)):
                    continue

                if obj.__module__ == ModuleExplorerRealmCodecRegistry.__module__:
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                concept_type = figure_out_concept(cast(type, obj))
                if concept_type is None:
                    raise Exception(
                        f"Could not infer concept class from decoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )
                realm_type = figure_out_realm(cast(type, obj))
                if realm_type is None:
                    raise Exception(
                        f"Could not infer realm class from decoder class {name} in {the_module.__name__} because inheritence is messed-up"
                    )

                yield concept_type, realm_type, cast(type, obj)

        registry = ModuleExplorerRealmCodecRegistry()

        registry._add_encoder(
            type(None), DatabaseRealm, _StandardPrimitiveDatabaseEncoder(type(None))
        )
        registry._add_decoder(
            type(None), DatabaseRealm, _StandardPrimitiveDatabaseDecoder(type(None))
        )

        registry._add_encoder(
            bool, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(bool)
        )
        registry._add_decoder(
            bool, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(bool)
        )

        registry._add_encoder(
            int, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(int)
        )
        registry._add_decoder(
            int, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(int)
        )

        registry._add_encoder(
            float, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(float)
        )
        registry._add_decoder(
            float, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(float)
        )

        registry._add_encoder(
            str, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(str)
        )
        registry._add_decoder(
            str, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(str)
        )

        registry._add_encoder(
            date, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(date)
        )
        registry._add_decoder(
            date, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(date)
        )

        registry._add_encoder(
            datetime, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(datetime)
        )
        registry._add_decoder(
            datetime, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(datetime)
        )

        registry._add_encoder(
            Date, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(Date)
        )
        registry._add_decoder(
            Date, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(Date)
        )

        registry._add_encoder(
            DateTime, DatabaseRealm, _StandardPrimitiveDatabaseEncoder(DateTime)
        )
        registry._add_decoder(
            DateTime, DatabaseRealm, _StandardPrimitiveDatabaseDecoder(DateTime)
        )

        registry._add_encoder(EntityId, DatabaseRealm, EntityIdDatabaseEncoder())
        registry._add_encoder(EntityId, WebRealm, EntityIdWebEncoder())
        registry._add_decoder(EntityId, DatabaseRealm, EntityIdDatabaseDecoder())

        registry._add_encoder(
            EntityName, DatabaseRealm, EntityNameDatabaseEncoder(EntityName)
        )
        registry._add_decoder(
            EntityName, DatabaseRealm, EntityNameDatabaseDecoder(EntityName)
        )

        registry._add_encoder(Timestamp, DatabaseRealm, TimestampDatabaseEncoder())
        registry._add_decoder(Timestamp, DatabaseRealm, TimestampDatabaseDecoder())

        registry._add_encoder(
            EventSource, DatabaseRealm, _StandardEnumValueDatabaseEncoder(EventSource)
        )
        registry._add_decoder(
            EventSource, DatabaseRealm, _StandardEnumValueDatabaseDecoder(EventSource)
        )

        for m in find_all_modules(*module_roots):
            for concept_type, realm_type, encoder_type in extract_concept_encoders(m):
                registry._add_encoder(
                    concept_type, realm_type, registry._build_encoder(encoder_type)
                )

            for concept_type, realm_type, decoder_type in extract_concept_decoders(m):
                registry._add_decoder(
                    concept_type, realm_type, registry._build_decoder(decoder_type)
                )

            for atomic_value_type in extract_atomic_values(m):
                if not allowed_in_realm(atomic_value_type, DatabaseRealm):
                    continue

                if not registry._has_encoder(atomic_value_type, DatabaseRealm):
                    if issubclass(atomic_value_type, EntityName):
                        registry._add_encoder(
                            atomic_value_type,
                            DatabaseRealm,
                            EntityNameDatabaseEncoder(atomic_value_type),
                        )
                    elif registry._has_encoder(atomic_value_type, DatabaseRealm):
                        continue
                    else:
                        raise Exception(f"No encoder for {atomic_value_type}")

                if not registry._has_decoder(atomic_value_type, DatabaseRealm):
                    if issubclass(atomic_value_type, EntityName):
                        registry._add_decoder(
                            atomic_value_type,
                            DatabaseRealm,
                            EntityNameDatabaseDecoder(atomic_value_type),
                        )
                    elif registry._has_decoder(atomic_value_type, DatabaseRealm):
                        continue
                    else:
                        raise Exception(f"No decoder for {atomic_value_type}")

            for composite_value_type in extract_composite_values(m):
                if not allowed_in_realm(composite_value_type, DatabaseRealm):
                    continue

                if not registry._has_encoder(composite_value_type, DatabaseRealm):
                    registry._add_encoder(
                        composite_value_type,
                        DatabaseRealm,
                        _StandardCompositeValueEncoder(
                            registry, composite_value_type, DatabaseRealm
                        ),
                    )

                if not registry._has_encoder(composite_value_type, CliRealm):
                    registry._add_encoder(
                        composite_value_type,
                        CliRealm,
                        _StandardCompositeValueEncoder(
                            registry, composite_value_type, CliRealm
                        ),
                    )

                if not registry._has_encoder(composite_value_type, WebRealm):
                    registry._add_encoder(
                        composite_value_type,
                        WebRealm,
                        _StandardCompositeValueEncoder(
                            registry, composite_value_type, WebRealm
                        ),
                    )

                if not registry._has_decoder(composite_value_type, DatabaseRealm):
                    registry._add_decoder(
                        composite_value_type,
                        DatabaseRealm,
                        _StandardCompositeValueDecoder(
                            registry, composite_value_type, DatabaseRealm
                        ),
                    )

                if not registry._has_decoder(composite_value_type, CliRealm):
                    registry._add_decoder(
                        composite_value_type,
                        CliRealm,
                        _StandardCompositeValueDecoder(
                            registry, composite_value_type, CliRealm
                        ),
                    )

                if not registry._has_decoder(composite_value_type, WebRealm):
                    registry._add_decoder(
                        composite_value_type,
                        WebRealm,
                        _StandardCompositeValueDecoder(
                            registry, composite_value_type, WebRealm
                        ),
                    )

            for enum_value_type in extract_enum_values(m):
                if not allowed_in_realm(enum_value_type, DatabaseRealm):
                    continue

                if not registry._has_encoder(enum_value_type, DatabaseRealm):
                    registry._add_encoder(
                        enum_value_type,
                        DatabaseRealm,
                        _StandardEnumValueDatabaseEncoder(enum_value_type),
                    )

                if not registry._has_decoder(enum_value_type, DatabaseRealm):
                    registry._add_decoder(
                        enum_value_type,
                        DatabaseRealm,
                        _StandardEnumValueDatabaseDecoder(enum_value_type),
                    )

            for entity in extract_entities(m):
                if not allowed_in_realm(entity, DatabaseRealm):
                    continue

                if not registry._has_encoder(entity, DatabaseRealm):
                    registry._add_encoder(
                        entity,
                        DatabaseRealm,
                        _StandardEntityEncoder(registry, entity, DatabaseRealm),
                    )

                if not registry._has_encoder(entity, CliRealm):
                    registry._add_encoder(
                        entity,
                        CliRealm,
                        _StandardEntityEncoder(registry, entity, CliRealm),
                    )

                if not registry._has_encoder(entity, WebRealm):
                    registry._add_encoder(
                        entity,
                        WebRealm,
                        _StandardEntityEncoder(registry, entity, WebRealm),
                    )

                if not registry._has_decoder(entity, DatabaseRealm):
                    registry._add_decoder(
                        entity,
                        DatabaseRealm,
                        _StandardEntityDecoder(registry, entity, DatabaseRealm),
                    )

                if not registry._has_decoder(entity, CliRealm):
                    registry._add_decoder(
                        entity,
                        CliRealm,
                        _StandardEntityDecoder(registry, entity, CliRealm),
                    )

                if not registry._has_decoder(entity, WebRealm):
                    registry._add_decoder(
                        entity,
                        WebRealm,
                        _StandardEntityDecoder(registry, entity, WebRealm),
                    )

            for record in extract_records(m):
                if not allowed_in_realm(record, DatabaseRealm):
                    continue

                if not registry._has_encoder(record, DatabaseRealm):
                    registry._add_encoder(
                        record,
                        DatabaseRealm,
                        _StandardRecordEncoder(registry, record, DatabaseRealm),
                    )

                if not registry._has_encoder(record, CliRealm):
                    registry._add_encoder(
                        record,
                        CliRealm,
                        _StandardRecordEncoder(registry, record, CliRealm),
                    )

                if not registry._has_encoder(record, WebRealm):
                    registry._add_encoder(
                        record,
                        WebRealm,
                        _StandardRecordEncoder(registry, record, WebRealm),
                    )

                if not registry._has_decoder(record, DatabaseRealm):
                    registry._add_decoder(
                        record,
                        DatabaseRealm,
                        _StandardRecordDecoder(registry, record, DatabaseRealm),
                    )

                if not registry._has_decoder(record, CliRealm):
                    registry._add_decoder(
                        record,
                        CliRealm,
                        _StandardRecordDecoder(registry, record, CliRealm),
                    )

                if not registry._has_decoder(record, WebRealm):
                    registry._add_decoder(
                        record,
                        WebRealm,
                        _StandardRecordDecoder(registry, record, WebRealm),
                    )

            for use_case_args in extract_use_case_args(m):
                if not allowed_in_realm(use_case_args, CliRealm):
                    continue

                if not registry._has_encoder(use_case_args, EventStoreRealm):
                    registry._add_encoder(
                        use_case_args,
                        EventStoreRealm,
                        _StandardUseCaseArgsEventStoreEncoder(registry, use_case_args),
                    )

                if not registry._has_decoder(use_case_args, CliRealm):
                    registry._add_decoder(
                        use_case_args,
                        CliRealm,
                        _StandardUseCaseArgsCliDecoder(registry, use_case_args),
                    )

                if not registry._has_decoder(use_case_args, WebRealm):
                    registry._add_decoder(
                        use_case_args,
                        WebRealm,
                        _StandardUseCaseArgsWebDecoder(registry, use_case_args),
                    )

            for use_case_result in extract_use_case_result(m):
                if not allowed_in_realm(use_case_args, WebRealm):
                    continue

                if not registry._has_encoder(use_case_result, WebRealm):
                    registry._add_encoder(
                        use_case_result,
                        WebRealm,
                        _StandardUseCaseResultWebEncoder(registry, use_case_result),
                    )

        return registry

    def get_all_registered_types(
        self, base_type: type[_DomainThingT], realm: type[Realm]
    ) -> Iterator[type[_DomainThingT]]:
        r"""Get all types registered that derive from base type."""
        yielded_types: set[type[Thing]] = set()

        for (the_type, type_realm) in self._encoders_registry.keys():
            if the_type in yielded_types:
                continue
            if not allowed_in_realm(the_type, realm):
                continue
            if issubclass(the_type, base_type) and (
                type_realm is realm or type_realm is DatabaseRealm
            ):
                yielded_types.add(the_type)
                yield the_type

        for (the_type, type_realm) in self._decoders_registry.keys():
            if the_type in yielded_types:
                continue
            if not allowed_in_realm(the_type, realm):
                continue
            if issubclass(the_type, base_type) and (
                type_realm is realm or type_realm is DatabaseRealm
            ):
                yielded_types.add(the_type)
                yield the_type

    def get_encoder(
        self,
        thing_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[_DomainThingT] | None = None,
    ) -> RealmEncoder[_DomainThingT, _RealmT]:
        """Get a codec for a realm and a thing type."""
        if isinstance(thing_type, typing._GenericAlias) and thing_type.__name__ == "Literal":  # type: ignore
            return cast(
                RealmEncoder[_DomainThingT, _RealmT],
                _LiteralEncoder(thing_type.__args__, realm),
            )  # type: ignore
        elif isinstance(thing_type, ForwardRef):
            if root_type is None:
                raise Exception("Cannot infer the type of a string without a root type")
            if f"'{root_type.__name__}'" not in str(thing_type):
                raise Exception(
                    f"Recursive types are only allowed to be encoded as root types, but {thing_type} is not the root type {root_type.__name__}"
                )
            return self.get_encoder(root_type, realm, root_type)
        elif isinstance(thing_type, str):
            if root_type is None:
                raise Exception("Cannot infer the type of a string without a root type")
            if thing_type != root_type.__name__:
                raise Exception(
                    f"Recursive types are only allowed to be encoded as root types, but {thing_type} is not the root type {root_type.__name__}"
                )
            return self.get_encoder(root_type, realm, root_type)
        elif is_thing_ish_type(thing_type):
            if (thing_type, realm) not in self._encoders_registry:
                if (thing_type, DatabaseRealm) not in self._encoders_registry:
                    raise Exception(
                        f"Could not find encoder for realm {realm} and thing {thing_type.__name__}"
                    )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    self._encoders_registry[
                        cast(
                            tuple[type[Thing], type[Realm]], (thing_type, DatabaseRealm)
                        )
                    ],
                )
            return cast(
                RealmEncoder[_DomainThingT, _RealmT],
                self._encoders_registry[
                    cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
                ],
            )
        elif (thing_type_origin := get_origin(thing_type)) is not None:
            if thing_type_origin is typing.Union or (
                isinstance(thing_type_origin, type)
                and issubclass(thing_type_origin, types.UnionType)
            ):
                field_args = cast(
                    list[type[DomainThing] | ForwardRef | str], get_args(thing_type)
                )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    _UnionEncoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        field_args,
                        realm,
                    ),
                )
            elif thing_type_origin is UpdateAction and realm is EventStoreRealm:
                update_action_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    _UpdateActionEventStoreEncoder(
                        self,
                        cast(type[DomainThing], root_type),
                        update_action_type,
                        realm,
                    ),
                )
            elif thing_type_origin is list:
                list_item_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    _ListEncoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        list_item_type,
                        realm,
                    ),
                )
            elif thing_type_origin is set:
                set_item_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    _SetEncoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        set_item_type,
                        realm,
                    ),
                )
            elif thing_type_origin is dict:
                dict_key_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                dict_value_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[1]
                )
                return cast(
                    RealmEncoder[_DomainThingT, _RealmT],
                    _DictEncoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        dict_key_type,
                        dict_value_type,
                        realm,
                    ),
                )
            else:
                raise Exception(
                    f"Could not find encoder for realm {realm} and thing {thing_type.__name__}"
                )
        else:
            raise Exception(
                f"Could not find encoder for realm {realm} and thing {thing_type.__name__}"
            )

    def get_decoder(
        self,
        thing_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[_DomainThingT] | None = None,
    ) -> RealmDecoder[_DomainThingT, _RealmT]:
        """Get a codec for a realm and a thing type."""
        if isinstance(thing_type, typing._GenericAlias) and thing_type.__name__ == "Literal":  # type: ignore
            return cast(RealmDecoder[_DomainThingT, _RealmT], _LiteralDecoder(thing_type.__args__, realm))  # type: ignore
        elif isinstance(thing_type, ForwardRef):
            if root_type is None:
                raise Exception("Cannot infer the type of a string without a root type")
            if f"'{root_type.__name__}'" not in str(thing_type):
                raise Exception(
                    f"Recursive types are only allowed to be encoded as root types, but {thing_type} is not the root type {root_type.__name__}"
                )
            return self.get_decoder(root_type, realm, root_type)
        elif isinstance(thing_type, str):
            if root_type is None:
                raise Exception("Cannot infer the type of a string without a root type")
            if thing_type != root_type.__name__:
                raise Exception(
                    f"Recursive types are only allowed to be encoded as root types, but {thing_type} is not the root type {root_type.__name__}"
                )
            return self.get_decoder(root_type, realm, root_type)
        elif is_thing_ish_type(thing_type):
            if (thing_type, realm) not in self._decoders_registry:
                if (thing_type, DatabaseRealm) not in self._decoders_registry:
                    raise Exception(
                        f"Could not find decoder for realm {realm} and thing {thing_type.__name__}"
                    )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    self._decoders_registry[
                        cast(
                            tuple[type[Thing], type[Realm]], (thing_type, DatabaseRealm)
                        )
                    ],
                )
            return cast(
                RealmDecoder[_DomainThingT, _RealmT],
                self._decoders_registry[
                    cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
                ],
            )
        elif (thing_type_origin := get_origin(thing_type)) is not None:
            if thing_type_origin is typing.Union or (
                isinstance(thing_type_origin, type)
                and issubclass(thing_type_origin, types.UnionType)
            ):
                field_args = cast(
                    list[type[DomainThing] | ForwardRef | str], get_args(thing_type)
                )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    _UnionDecoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        field_args,
                        realm,
                    ),
                )
            elif thing_type_origin is UpdateAction and realm is WebRealm:
                update_action_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    _UpdateActionWebDecoder(
                        self,
                        cast(type[DomainThing], root_type),
                        update_action_type,
                        realm,
                    ),
                )
            elif thing_type_origin is list:
                list_item_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    _ListDecoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        list_item_type,
                        realm,
                    ),
                )
            elif thing_type_origin is set:
                set_item_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    _SetDecoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        set_item_type,
                        realm,
                    ),
                )
            elif thing_type_origin is dict:
                dict_key_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[0]
                )
                dict_value_type = cast(
                    type[DomainThing] | ForwardRef | str, get_args(thing_type)[1]
                )
                return cast(
                    RealmDecoder[_DomainThingT, _RealmT],
                    _DictDecoder(
                        self,
                        cast(type[DomainThing] | None, root_type),
                        dict_key_type,
                        dict_value_type,
                        realm,
                    ),
                )
            else:
                raise Exception(
                    f"Could not find decoder for realm {realm} and thing {thing_type.__name__}"
                )
        else:
            raise Exception(
                f"Could not find decoder for realm {realm} and thing {thing_type.__name__}"
            )

    def _has_encoder(
        self,
        thing_type: type[_DomainThingT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a thing type."""
        return (thing_type, realm) in self._encoders_registry

    def _add_encoder(
        self,
        thing_type: type[_DomainThingT],
        realm: type[_RealmT],
        encoder: RealmEncoder[_DomainThingT, _RealmT],
    ) -> None:
        """Add a codec for a realm and a thing type."""
        if self._has_encoder(thing_type, realm):
            raise Exception(
                f"Duplicate encoder for realm {realm} and thing {thing_type.__name__}"
            )
        self._encoders_registry[
            cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
        ] = cast(RealmEncoder[Thing, Realm], encoder)

    def _has_decoder(
        self,
        thing_type: type[_DomainThingT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a thing type."""
        return (thing_type, realm) in self._decoders_registry

    def _add_decoder(
        self,
        thing_type: type[_DomainThingT],
        realm: type[_RealmT],
        decoder: RealmDecoder[_DomainThingT, _RealmT],
    ) -> None:
        """Add a codec for a realm and a thing type."""
        if self._has_decoder(thing_type, realm):
            raise Exception(
                f"Duplicate decoder for realm {realm} and thing {thing_type.__name__}"
            )
        self._decoders_registry[
            cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
        ] = cast(RealmDecoder[Thing, Realm], decoder)

    def _build_encoder(
        self, encoder_type: type[RealmEncoder[Concept, Realm]]
    ) -> RealmEncoder[Concept, Realm]:
        new_encoder = encoder_type()
        for name in new_encoder.__class__.__dict__:
            if name != "_realm_codec_registry":
                continue
            codec_registry_ref = getattr(new_encoder, name)
            if codec_registry_ref is not PROVIDE_VIA_REGISTRY:
                continue
            setattr(new_encoder, name, self)
        return new_encoder

    def _build_decoder(
        self, decoder_type: type[RealmDecoder[Concept, Realm]]
    ) -> RealmDecoder[Concept, Realm]:
        new_decoder = decoder_type()
        for name in new_decoder.__class__.__dict__:
            if name != "_realm_codec_registry":
                continue
            codec_registry_ref = getattr(new_decoder, name)
            if codec_registry_ref is not PROVIDE_VIA_REGISTRY:
                continue
            setattr(new_decoder, name, self)
        return new_decoder
