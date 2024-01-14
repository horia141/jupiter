"""Application-specific realm helpers."""
from collections.abc import Mapping
import dataclasses
from datetime import date, datetime
import importlib
import pkgutil
import types
import typing
from types import GenericAlias, ModuleType
from typing import Final, Generic, Iterator, TypeVar, cast, get_args, get_origin

from jupiter.core.framework.base.entity_id import (
    EntityId,
    EntityIdDatabaseDecoder,
    EntityIdDatabaseEncoder,
)
from jupiter.core.framework.base.entity_name import (
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
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    DatabaseRealm,
    Realm,
    RealmCodecRegistry,
    RealmConcept,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
)
from jupiter.core.framework.record import Record
from jupiter.core.framework.value import AtomicValue, CompositeValue, EnumValue
from pendulum.date import Date
from pendulum.datetime import DateTime

_RealmT = TypeVar("_RealmT", bound=Realm)
_ConceptT = TypeVar("_ConceptT", bound=Concept)
_AtomicValueT = TypeVar("_AtomicValueT", bound=AtomicValue)
_CompositeValueT = TypeVar("_CompositeValueT", bound=CompositeValue)
_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)
_EntityT = TypeVar("_EntityT", bound=Entity)
_RecordT = TypeVar("_RecordT", bound=Record)


class _StandardAtomicValueDatabaseEncoder(
    Generic[_AtomicValueT], RealmEncoder[_AtomicValueT, DatabaseRealm]
):
    """An encoder for atomic values."""

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _AtomicValueT) -> RealmConcept:
        """Encode a realm to a string."""
        return value.to_primitive()


class _StandardAtomicValueDatabaseDecoder(
    Generic[_AtomicValueT], RealmDecoder[_AtomicValueT, DatabaseRealm]
):
    """A decoder for atomic values."""

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _AtomicValueT:
        """Decode a realm from a string."""
        if not isinstance(value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} in {self.__class__} to be primitive"
            )

        return self._the_type.from_raw(value)


class _StandardCompositeValueDatabaseEncoder(
    Generic[_CompositeValueT], RealmEncoder[_CompositeValueT, DatabaseRealm]
):
    """An encoder for composite values."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_CompositeValueT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_CompositeValueT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def encode(self, value: _CompositeValueT) -> RealmConcept:
        """Encode a realm to a string."""
        result: dict[str, RealmConcept] = {}
        all_fields = dataclasses.fields(self._the_type)
        for field in all_fields:
            field_value = getattr(value, field.name)
            if isinstance(
                field_value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)
            ):
                result[field.name] = field_value
            elif isinstance(field_value, (AtomicValue, CompositeValue, EnumValue)):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, list):
                if len(field_value) == 0:
                    result[field.name] = []
                else:
                    if isinstance(
                        field_value[0],
                        (type(None), bool, int, float, str, date, datetime, Date, DateTime),
                    ):
                        result[field.name] = [v for v in field_value]
                    else:
                        list_item_encoder = self._realm_codec_registry.get_encoder(
                            field_value[0].__class__, DatabaseRealm
                        )
                        result[field.name] = [
                            list_item_encoder.encode(v) for v in field_value
                        ]
            else:
                raise Exception(
                    f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                )
        return result


class _StandardCompositeValueDatabaseDecoder(
    Generic[_CompositeValueT], RealmDecoder[_CompositeValueT, DatabaseRealm]
):
    """A decoder for composite values."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_CompositeValueT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_CompositeValueT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _CompositeValueT:
        if not isinstance(value, dict):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be a dict object"
            )

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[str, Primitive | Concept | list[Primitive] | list[Concept]] = {}

        for field in all_fields:
            if field.name not in value:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            field_value = value[field.name]

            if field.type in (type(None), bool, int, float, str, date, datetime, Date, DateTime):
                if type(field_value) is not field.type:
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be {field.type} but was {type(field_value)}"
                    )
                ctor_args[field.name] = None
            elif (
                isinstance(field.type, type)
                and get_origin(field.type) is None
                and issubclass(field.type, (AtomicValue, CompositeValue, EnumValue))
            ):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif isinstance(field.type, type) and get_origin(field.type) is list:
                list_item_type = cast(
                    type[Primitive | Concept], get_args(field.type)[0]
                )
                if not isinstance(field_value, list):
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                    )
                if len(field_value) == 0:
                    ctor_args[field.name] = []
                else:
                    if list_item_type in (
                        type(None),
                        bool,
                        int,
                        float,
                        str,
                        date, datetime, 
                        Date,
                        DateTime,
                    ):
                        ctor_value_primitive: list[Primitive] = []
                        for list_item in field_value:
                            if type(list_item) is not list_item_type:
                                raise RealmDecodingError(
                                    f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list of {list_item_type}"
                                )
                            ctor_value_primitive.append(cast(Primitive, list_item))
                        ctor_args[field.name] = ctor_value_primitive
                    else:
                        ctor_value_concept = []
                        list_item_decoder: RealmDecoder[
                            Concept, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            cast(type[Concept], list_item_type), DatabaseRealm
                        )
                        for list_item in field_value:
                            ctor_value_concept.append(
                                list_item_decoder.decode(list_item)
                            )
                        ctor_args[field.name] = ctor_value_concept
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and (
                        field_args[0] is type(None) and field_args[1] is not type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[1], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    elif len(field_args) == 2 and (
                        field_args[1] is type(None) and field_args[0] is not type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[0], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    else:
                        raise Exception("Not implemented - union")
                else:
                    raise Exception(
                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                    )
            else:
                raise Exception(
                    f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                )

        return self._the_type(**ctor_args)


class _StandardEnumValueDatabaseEncoder(
    Generic[_EnumValueT], RealmEncoder[_EnumValueT, DatabaseRealm]
):

    _the_type: type[_EnumValueT]

    def __init__(self, the_type: type[_EnumValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _EnumValueT) -> RealmConcept:
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

    def decode(self, value: RealmConcept) -> _EnumValueT:
        """Decode a realm from a string."""
        if not isinstance(value, str):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be string"
            )

        value_clean: str = value.strip().lower()

        try:
            return cast(_EnumValueT, self._the_type(value_clean))
        except ValueError:
            raise RealmDecodingError(
                f"Expected enum {self._the_type.__name__} '{value}' to be one of '{','.join(str(s.value) for s in self._the_type)}'",
            ) from None


class _StandardEntityDatabaseEncoder(
    Generic[_EntityT], RealmEncoder[_EntityT, DatabaseRealm]
):
    """An encoder for entities."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_EntityT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_EntityT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def encode(self, value: _EntityT) -> RealmConcept:
        """Encode an entity."""
        result: dict[str, RealmConcept] = {}
        all_fields = dataclasses.fields(value)
        for field in all_fields:
            field_value = getattr(value, field.name)
            if field.name == "events":
                continue
            if isinstance(
                field_value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)
            ):
                result[field.name] = field_value
            elif isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            elif isinstance(field_value, (AtomicValue, CompositeValue, EnumValue)):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, list):
                if len(field_value) == 0:
                    result[field.name] = []
                else:
                    if isinstance(
                        field_value[0],
                        (type(None), bool, int, float, str, date, datetime, Date, DateTime),
                    ):
                        result[field.name] = [v for v in field_value]
                    else:
                        list_item_encoder = self._realm_codec_registry.get_encoder(
                            field_value[0].__class__, DatabaseRealm
                        )
                        result[field.name] = [
                            list_item_encoder.encode(v) for v in field_value
                        ]
            else:
                raise Exception(
                    f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                )
        return result


class _StandardEntityDatabaseDecoder(
    Generic[_EntityT], RealmDecoder[_EntityT, DatabaseRealm]
):
    """A decoder for entities."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_EntityT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_EntityT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _EntityT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[
            str, Primitive | ParentLink | Concept | list[Primitive] | list[Concept]
        ] = {}

        entity_id_decoder = self._realm_codec_registry.get_decoder(
            EntityId, DatabaseRealm
        )
        timestamp_decoder = self._realm_codec_registry.get_decoder(
            Timestamp, DatabaseRealm
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

            if field.name in value:
                field_value = value[field.name]
            elif field.type is ParentLink and field.name + "_ref_id" in value:
                field_value = value[field.name + "_ref_id"]
            else:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            if field.type in (type(None), bool, int, float, str, date, datetime, Date, DateTime):
                if type(field_value) is not field.type:
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be {field.type} but was {type(field_value)}"
                    )
                ctor_args[field.name] = None
            elif field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            elif (
                isinstance(field.type, type)
                and get_origin(field.type) is None
                and issubclass(field.type, (AtomicValue, CompositeValue, EnumValue))
            ):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif isinstance(field.type, type) and issubclass(field.type, list):
                list_item_type = cast(
                    type[Primitive | Concept], get_args(field.type)[0]
                )
                if not isinstance(field_value, list):
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                    )
                if len(field_value) == 0:
                    ctor_args[field.name] = []
                else:
                    if list_item_type in (
                        type(None),
                        bool,
                        int,
                        float,
                        str,date, datetime, 
                        Date,
                        DateTime,
                    ):
                        ctor_value_primitive: list[Primitive] = []
                        for list_item in field_value:
                            if type(list_item) is not list_item_type:
                                raise RealmDecodingError(
                                    f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list of {list_item_type}"
                                )
                            ctor_value_primitive.append(cast(Primitive, list_item))
                        ctor_args[field.name] = ctor_value_primitive
                    else:
                        ctor_value_concept = []
                        list_item_decoder: RealmDecoder[
                            Concept, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            cast(type[Concept], list_item_type), DatabaseRealm
                        )
                        for list_item in field_value:
                            ctor_value_concept.append(
                                list_item_decoder.decode(list_item)
                            )
                        ctor_args[field.name] = ctor_value_concept
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and (
                        field_args[0] is type(None) and field_args[1] is not type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[1], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    elif len(field_args) == 2 and (
                        field_args[1] is type(None) and field_args[0] is not type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[0], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    else:
                        raise Exception("Not implemented - union")
                else:
                    raise Exception(
                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                    )
            else:
                raise Exception(
                    f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                )

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


class _StandardRecordDatabaseEncoder(
    Generic[_RecordT], RealmEncoder[_RecordT, DatabaseRealm]
):
    """An encoder for records."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_RecordT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_RecordT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def encode(self, value: _RecordT) -> RealmConcept:
        """Encode a record."""
        result: dict[str, RealmConcept] = {}
        all_fields = dataclasses.fields(value)
        for field in all_fields:
            field_value = getattr(value, field.name)
            if isinstance(
                field_value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)
            ):
                result[field.name] = field_value
            elif isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            elif isinstance(field_value, (AtomicValue, CompositeValue, EnumValue)):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, list):
                if len(field_value) == 0:
                    result[field.name] = []
                else:
                    if isinstance(
                        field_value[0],
                        (type(None), bool, int, float, str, date, datetime, Date, DateTime),
                    ):
                        result[field.name] = [v for v in field_value]
                    else:
                        list_item_encoder = self._realm_codec_registry.get_encoder(
                            field_value[0].__class__, DatabaseRealm
                        )
                        result[field.name] = [
                            list_item_encoder.encode(v) for v in field_value
                        ]
            else:
                raise Exception(
                    f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                )
        return result


class _StandardRecordDatabaseDecoder(
    Generic[_RecordT], RealmDecoder[_RecordT, DatabaseRealm]
):
    """A decoder for records."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _the_type: type[_RecordT]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, the_type: type[_RecordT]
    ) -> None:
        self._realm_codec_registry = realm_codec_registry
        self._the_type = the_type

    def decode(self, value: RealmConcept) -> _RecordT:
        if not isinstance(value, dict):
            raise RealmDecodingError("Expected value to be a dictionary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[
            str, Primitive | ParentLink | Concept | list[Primitive] | list[Concept]
        ] = {}

        entity_id_decoder = self._realm_codec_registry.get_decoder(
            EntityId, DatabaseRealm
        )
        timestamp_decoder = self._realm_codec_registry.get_decoder(
            Timestamp, DatabaseRealm
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

            if field.type in (type(None), bool, int, float, str, date, datetime, Date, DateTime):
                if type(field_value) is not field.type:
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be {field.type} but was {type(field_value)}"
                    )
                ctor_args[field.name] = None
            elif field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            elif (
                isinstance(field.type, type)
                and get_origin(field.type) is None
                and issubclass(field.type, (AtomicValue, CompositeValue, EnumValue))
            ):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif isinstance(field.type, type) and issubclass(field.type, list):
                list_item_type = cast(
                    type[Primitive | Concept], get_args(field.type)[0]
                )
                if not isinstance(field_value, list):
                    raise RealmDecodingError(
                        f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                    )
                if len(field_value) == 0:
                    ctor_args[field.name] = []
                else:
                    if list_item_type in (
                        type(None),
                        bool,
                        int,
                        float,
                        str,date, datetime, 
                        Date,
                        DateTime,
                    ):
                        ctor_value_primitive: list[Primitive] = []
                        for list_item in field_value:
                            if type(list_item) is not list_item_type:
                                raise RealmDecodingError(
                                    f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list of {list_item_type}"
                                )
                            ctor_value_primitive.append(cast(Primitive, list_item))
                        ctor_args[field.name] = ctor_value_primitive
                    else:
                        ctor_value_concept = []
                        list_item_decoder: RealmDecoder[
                            Concept, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            cast(type[Concept], list_item_type), DatabaseRealm
                        )
                        for list_item in field_value:
                            ctor_value_concept.append(
                                list_item_decoder.decode(list_item)
                            )
                        ctor_args[field.name] = ctor_value_concept
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and (
                        field_args[0] is type(None) and field_args[1] is not type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[1], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    elif len(field_args) == 2 and (
                        field_args[0] is not type(None) and field_args[1] is type(None)
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[0], DatabaseRealm
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    else:
                        raise Exception("Not implemented - union")
                else:
                    raise Exception(
                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                    )
            else:
                raise Exception(
                    f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                )

        return self._the_type(
            created_time=created_time,
            last_modified_time=last_modified_time,
            **ctor_args,
        )


class ModuleExplorerRealmCodecRegistry(RealmCodecRegistry):
    """A registry for realm codecs constructed by exploring a module tree."""

    _encoders_registry: Final[
        dict[tuple[type[Concept], type[Realm]], RealmEncoder[Concept, Realm]]
    ]
    _decoders_registry: Final[
        dict[tuple[type[Concept], type[Realm]], RealmDecoder[Concept, Realm]]
    ]

    def __init__(
        self,
    ) -> None:
        """Initialize the registry."""
        self._encoders_registry = {}
        self._decoders_registry = {}

    @staticmethod
    def build_from_module_root(
        module_root: ModuleType,
    ) -> "ModuleExplorerRealmCodecRegistry":
        """Build a registry from a module root using magick."""

        def find_all_modules() -> list[ModuleType]:
            all_modules = []

            def explore_module_tree(the_module: ModuleType) -> None:
                for _, name, is_pkg in pkgutil.iter_modules(the_module.__path__):
                    full_name = the_module.__name__ + "." + name
                    all_modules.append(importlib.import_module(full_name))
                    if is_pkg:
                        submodule = getattr(the_module, name)
                        explore_module_tree(submodule)

            explore_module_tree(module_root)
            return all_modules

        def extract_atomic_values(
            the_module: ModuleType,
        ) -> Iterator[type[AtomicValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, AtomicValue)):
                    continue

                yield obj

        def extract_composite_values(
            the_module: ModuleType,
        ) -> Iterator[type[CompositeValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, CompositeValue)):
                    continue

                yield obj

        def extract_enum_values(
            the_module: ModuleType,
        ) -> Iterator[type[EnumValue]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, EnumValue)):
                    continue

                yield obj

        def extract_entities(
            the_module: ModuleType,
        ) -> Iterator[type[Entity]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Entity)):
                    continue

                yield obj

        def extract_records(
            the_module: ModuleType,
        ) -> Iterator[type[Record]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Record)):
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

        def extract_realm_encoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmEncoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__"):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmEncoder)):
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

        def extract_realm_decoders(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[type[Concept], type[Realm], type[RealmDecoder[Concept, Realm]]]
        ]:
            for name, obj in the_module.__dict__.items():
                if not hasattr(obj, "__parameters__"):
                    continue

                if len(obj.__parameters__) > 0:
                    # This is not a concret type and we can move on
                    continue

                if not (isinstance(obj, type) and issubclass(obj, RealmDecoder)):
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

        registry._add_encoder(EntityId, DatabaseRealm, EntityIdDatabaseEncoder())
        registry._add_decoder(EntityId, DatabaseRealm, EntityIdDatabaseDecoder())

        registry._add_encoder(Timestamp, DatabaseRealm, TimestampDatabaseEncoder())
        registry._add_decoder(Timestamp, DatabaseRealm, TimestampDatabaseDecoder())

        for m in find_all_modules():
            for concept_type, realm_type, encoder_type in extract_realm_encoders(m):
                registry._add_encoder(concept_type, realm_type, encoder_type())

            for concept_type, realm_type, decoder_type in extract_realm_decoders(m):
                registry._add_decoder(concept_type, realm_type, decoder_type())

            for atomic_value_type in extract_atomic_values(m):
                if not registry._has_encoder(atomic_value_type, DatabaseRealm):
                    if issubclass(atomic_value_type, EntityName):
                        registry._add_encoder(
                            atomic_value_type,
                            DatabaseRealm,
                            EntityNameDatabaseEncoder(atomic_value_type),
                        )
                    else:
                        registry._add_encoder(
                            atomic_value_type,
                            DatabaseRealm,
                            _StandardAtomicValueDatabaseEncoder(atomic_value_type),
                        )

                if not registry._has_decoder(atomic_value_type, DatabaseRealm):
                    if issubclass(atomic_value_type, EntityName):
                        registry._add_decoder(
                            atomic_value_type,
                            DatabaseRealm,
                            EntityNameDatabaseDecoder(atomic_value_type),
                        )
                    else:
                        registry._add_decoder(
                            atomic_value_type,
                            DatabaseRealm,
                            _StandardAtomicValueDatabaseDecoder(atomic_value_type),
                        )

            for composite_value_type in extract_composite_values(m):
                if not registry._has_encoder(composite_value_type, DatabaseRealm):
                    registry._add_encoder(
                        composite_value_type,
                        DatabaseRealm,
                        _StandardCompositeValueDatabaseEncoder(
                            registry, composite_value_type
                        ),
                    )

                if not registry._has_decoder(composite_value_type, DatabaseRealm):
                    registry._add_decoder(
                        composite_value_type,
                        DatabaseRealm,
                        _StandardCompositeValueDatabaseDecoder(
                            registry, composite_value_type
                        ),
                    )

            for enum_value_type in extract_enum_values(m):
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
                if not registry._has_encoder(entity, DatabaseRealm):
                    registry._add_encoder(
                        entity,
                        DatabaseRealm,
                        _StandardEntityDatabaseEncoder(registry, entity),
                    )

                if not registry._has_decoder(entity, DatabaseRealm):
                    registry._add_decoder(
                        entity,
                        DatabaseRealm,
                        _StandardEntityDatabaseDecoder(registry, entity),
                    )

            for record in extract_records(m):
                if not registry._has_encoder(record, DatabaseRealm):
                    registry._add_encoder(
                        record,
                        DatabaseRealm,
                        _StandardRecordDatabaseEncoder(registry, record),
                    )

                if not registry._has_decoder(record, DatabaseRealm):
                    registry._add_decoder(
                        record,
                        DatabaseRealm,
                        _StandardRecordDatabaseDecoder(registry, record),
                    )

        return registry

    def get_encoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmEncoder[_ConceptT, _RealmT]:
        """Get a codec for a realm and a concept type."""
        if (concept_type, realm) not in self._encoders_registry:
            raise Exception(
                f"Could not find encoder for realm {realm} and concept {concept_type.__name__}"
            )
        return cast(
            RealmEncoder[_ConceptT, _RealmT],
            self._encoders_registry[(concept_type, realm)],
        )

    def get_decoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmDecoder[_ConceptT, _RealmT]:
        """Get a codec for a realm and a concept type."""
        if (concept_type, realm) not in self._decoders_registry:
            raise Exception(
                f"Could not find decoder for realm {realm} and concept {concept_type.__name__}"
            )
        return cast(
            RealmDecoder[_ConceptT, _RealmT],
            self._decoders_registry[(concept_type, realm)],
        )

    def _has_encoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a concept type."""
        return (concept_type, realm) in self._encoders_registry

    def _add_encoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
        encoder: RealmEncoder[_ConceptT, _RealmT],
    ) -> None:
        """Add a codec for a realm and a concept type."""
        if self._has_encoder(concept_type, realm):
            raise Exception(
                f"Duplicate encoder for realm {realm} and concept {concept_type.__name__}"
            )
        self._encoders_registry[(concept_type, realm)] = cast(
            RealmEncoder[Concept, Realm], encoder
        )

    def _has_decoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a concept type."""
        return (concept_type, realm) in self._decoders_registry

    def _add_decoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
        decoder: RealmDecoder[_ConceptT, _RealmT],
    ) -> None:
        """Add a codec for a realm and a concept type."""
        if self._has_decoder(concept_type, realm):
            raise Exception(
                f"Duplicate decoder for realm {realm} and concept {concept_type.__name__}"
            )
        self._decoders_registry[(concept_type, realm)] = cast(
            RealmDecoder[Concept, Realm], decoder
        )
