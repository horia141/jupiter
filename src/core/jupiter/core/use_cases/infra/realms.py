"""Application-specific realm helpers."""
import dataclasses
import types
import typing
from collections.abc import Mapping
from datetime import date, datetime
from types import GenericAlias, ModuleType
from typing import (
    Final,
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
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import (
    PROVIDE_VIA_REGISTRY,
    CliRealm,
    DatabaseRealm,
    Realm,
    RealmCodecRegistry,
    RealmDecoder,
    RealmDecodingError,
    RealmEncoder,
    RealmThing,
)
from jupiter.core.framework.record import Record
from jupiter.core.framework.thing import Thing, is_value_ish, is_value_ish_type
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case_io import UseCaseArgsBase
from jupiter.core.framework.utils import find_all_modules
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
)
from pendulum.date import Date
from pendulum.datetime import DateTime

_RealmT = TypeVar("_RealmT", bound=Realm)
_ThingT = TypeVar("_ThingT", bound=Thing)
_PrimitiveT = TypeVar("_PrimitiveT", bound=Primitive)
_AtomicValueT = TypeVar("_AtomicValueT", bound=AtomicValue)
_CompositeValueT = TypeVar("_CompositeValueT", bound=CompositeValue)
_EnumValueT = TypeVar("_EnumValueT", bound=EnumValue)
_EntityT = TypeVar("_EntityT", bound=Entity)
_RecordT = TypeVar("_RecordT", bound=Record)
_UseCaseArgsT = TypeVar("_UseCaseArgsT", bound=UseCaseArgsBase)


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


class _StandardAtomicValueDatabaseEncoder(
    Generic[_AtomicValueT], RealmEncoder[_AtomicValueT, DatabaseRealm]
):
    """An encoder for atomic values."""

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        """Initialize the encoder."""
        self._the_type = the_type

    def encode(self, value: _AtomicValueT) -> RealmThing:
        """Encode a realm to a string."""
        return value.to_primitive()


class _StandardAtomicValueDatabaseDecoder(
    Generic[_AtomicValueT], RealmDecoder[_AtomicValueT, DatabaseRealm]
):
    """A decoder for atomic values."""

    _the_type: type[_AtomicValueT]

    def __init__(self, the_type: type[_AtomicValueT]) -> None:
        self._the_type = the_type

    def decode(self, value: RealmThing) -> _AtomicValueT:
        """Decode a realm from a string."""
        if not isinstance(
            value, (type(None), bool, int, float, str, date, datetime, Date, DateTime)
        ):

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

    def encode(self, value: _CompositeValueT) -> RealmThing:
        """Encode a realm to a string."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(self._the_type)
        for field in all_fields:
            field_value = getattr(value, field.name)
            if is_value_ish(field_value):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, (list, set)):
                field_list_result = []
                for field_item in field_value:
                    if is_value_ish(field_item):
                        field_item_encoder = self._realm_codec_registry.get_encoder(
                            field_item.__class__, DatabaseRealm
                        )
                        field_list_result.append(field_item_encoder.encode(field_item))
                    elif isinstance(field_value, (list, set)):
                        field_subresult = []
                        for field_subitem in field_item:
                            if is_value_ish(field_subitem):
                                field_subitem_encoder = (
                                    self._realm_codec_registry.get_encoder(
                                        field_subitem.__class__, DatabaseRealm
                                    )
                                )
                                field_subresult.append(
                                    field_subitem_encoder.encode(field_subitem)
                                )
                            else:
                                raise Exception(
                                    f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                                )
                        field_list_result.append(field_subresult)
                    else:
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                result[field.name] = field_list_result
            elif isinstance(field_value, dict):
                field_dict_result = {}
                for field_key, field_item in field_value.items():
                    if not is_value_ish(field_key):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    if not is_value_ish(field_item):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    field_key_encoder = self._realm_codec_registry.get_encoder(
                        field_key.__class__, DatabaseRealm
                    )
                    field_item_encoder = self._realm_codec_registry.get_encoder(
                        field_item.__class__, DatabaseRealm
                    )
                    encoded_field_key = field_key_encoder.encode(field_key)

                    if not isinstance(encoded_field_key, str):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    field_dict_result[encoded_field_key] = field_item_encoder.encode(
                        field_item
                    )
                result[field.name] = field_dict_result
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

    def decode(self, value: RealmThing) -> _CompositeValueT:
        if not isinstance(value, dict):
            raise RealmDecodingError(
                f"Expected value for {self._the_type.__name__} to be a dict object"
            )

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[
            str,
            Thing | list[Thing] | set[Thing] | dict[Thing, Thing] | list[list[Thing]],
        ] = {}

        for field in all_fields:
            if field.name not in value:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            field_value = value[field.name]

            if isinstance(field.type, str) and field.type == self._the_type.__name__:  # type: ignore
                # A recursive type
                ctor_args[field.name] = self.decode(field_value)  # type: ignore
            elif is_value_ish_type(field.type):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif isinstance(field.type, typing._GenericAlias) and field.type.__name__ == "Literal":  # type: ignore
                if field_value not in field.type.__args__:
                    raise RealmDecodingError(
                        f"Expected value for {self._the_type.__name__} to be one of {field.type.__args__}"
                    )
                ctor_args[field.name] = field_value
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    for field_arg in field_args:
                        field_decoder = self._realm_codec_registry.get_decoder(
                            field_arg, DatabaseRealm
                        )
                        try:
                            ctor_args[field.name] = field_decoder.decode(field_value)
                            break
                        except (RealmDecodingError, InputValidationError):
                            pass
                    else:
                        raise RealmDecodingError(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is list:
                    list_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )

                    if isinstance(list_item_type, str) and list_item_type == self._the_type.__name__:  # type: ignore
                        # A recursive type
                        ctor_args[field.name] = [  # type: ignore
                            self.decode(item) for item in field_value
                        ]
                    elif is_value_ish_type(list_item_type):
                        list_item_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            list_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = [
                            list_item_decoder.decode(v) for v in field_value
                        ]
                    elif get_origin(list_item_type) is not None:
                        list_item_type_origin = get_origin(list_item_type)
                        if list_item_type_origin is typing.Union or (
                            isinstance(list_item_type_origin, type)
                            and issubclass(list_item_type_origin, types.UnionType)
                        ):
                            field_list_result = []
                            for field_item in field_value:
                                list_item_type_args = get_args(list_item_type)
                                for list_item_type_arg in list_item_type_args:
                                    list_item_decoder = (
                                        self._realm_codec_registry.get_decoder(
                                            list_item_type_arg, DatabaseRealm
                                        )
                                    )
                                    try:
                                        field_list_result.append(
                                            list_item_decoder.decode(field_item)
                                        )
                                        break
                                    except (RealmDecodingError, InputValidationError):
                                        pass
                                else:
                                    raise RealmDecodingError(
                                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                                    )
                            ctor_args[field.name] = field_list_result
                        elif list_item_type_origin is list:
                            list_item_item_type = cast(
                                type[Thing], get_args(list_item_type)[0]
                            )
                            if not isinstance(field_value, list):
                                raise RealmDecodingError(
                                    f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                                )
                            if isinstance(list_item_item_type, str) and list_item_item_type == self._the_type.__name__:  # type: ignore
                                # A recursive type
                                ctor_args[field.name] = [[self.decode(item) for item in item_list] for item_list in field_value]  # type: ignore
                            elif is_value_ish_type(list_item_item_type):
                                list_item_item_decoder: RealmDecoder[
                                    Thing, DatabaseRealm
                                ] = self._realm_codec_registry.get_decoder(
                                    list_item_item_type, DatabaseRealm
                                )
                                ctor_args[field.name] = [
                                    [
                                        list_item_item_decoder.decode(v)
                                        for v in item_list
                                    ]
                                    for item_list in field_value
                                ]
                            else:
                                raise Exception(
                                    f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                                )
                        else:
                            raise Exception(
                                f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                            )
                    else:
                        raise Exception(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is set:
                    set_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )

                    set_item_decoder: RealmDecoder[
                        Thing, DatabaseRealm
                    ] = self._realm_codec_registry.get_decoder(
                        set_item_type, DatabaseRealm
                    )
                    ctor_args[field.name] = set(
                        set_item_decoder.decode(v) for v in field_value
                    )
                elif field_type_origin is dict:
                    dict_key_type = cast(type[Thing], get_args(field.type)[0])
                    dict_value_type = cast(type[Thing], get_args(field.type)[1])
                    if not isinstance(field_value, dict):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a dict"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = {}
                    else:
                        dict_key_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_key_type, DatabaseRealm
                        )
                        dict_value_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_value_type, DatabaseRealm
                        )
                        ctor_args[field.name] = {
                            dict_key_decoder.decode(k): dict_value_decoder.decode(v)
                            for k, v in field_value.items()
                        }
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

    def encode(self, value: _EntityT) -> RealmThing:
        """Encode an entity."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(value.__class__)

        for field in all_fields:
            field_value = getattr(value, field.name)
            if field.name == "events":
                continue

            if is_value_ish(field_value):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            elif isinstance(field_value, (list, set)):
                field_list_result = []
                for field_item in field_value:
                    if not is_value_ish(field_item):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    field_item_encoder = self._realm_codec_registry.get_encoder(
                        field_item.__class__, DatabaseRealm
                    )
                    field_list_result.append(field_item_encoder.encode(field_item))
                result[field.name] = field_list_result
            elif isinstance(field_value, dict):
                field_dict_result = {}
                for field_key, field_item in field_value.items():
                    if not is_value_ish(field_key):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    if not is_value_ish(field_item):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    field_key_encoder = self._realm_codec_registry.get_encoder(
                        field_key.__class__, DatabaseRealm
                    )
                    field_item_encoder = self._realm_codec_registry.get_encoder(
                        field_item.__class__, DatabaseRealm
                    )
                    encoded_field_key = field_key_encoder.encode(field_key)

                    if not isinstance(encoded_field_key, str):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    field_dict_result[encoded_field_key] = field_item_encoder.encode(
                        field_item
                    )
                result[field.name] = field_dict_result
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

    def decode(self, value: RealmThing) -> _EntityT:
        if not isinstance(value, Mapping):
            raise RealmDecodingError("Expected value to be a dictonary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[
            str, ParentLink | Thing | list[Thing] | set[Thing] | dict[Thing, Thing]
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

            if is_value_ish_type(field.type):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    for field_arg in field_args:
                        if is_value_ish_type(field_arg):
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_arg, DatabaseRealm
                            )
                            try:
                                ctor_args[field.name] = field_decoder.decode(
                                    field_value
                                )
                                break
                            except (RealmDecodingError, InputValidationError):
                                pass
                        elif get_origin(field_arg) is not None:
                            field_arg_origin = get_origin(field_arg)

                            if field_arg_origin is list:
                                list_item_type = cast(
                                    type[Thing], get_args(field_arg)[0]
                                )
                                if not isinstance(field_value, list):
                                    continue
                                list_item_decoder = (
                                    self._realm_codec_registry.get_decoder(
                                        list_item_type, DatabaseRealm
                                    )
                                )
                                try:
                                    ctor_args[field.name] = [
                                        list_item_decoder.decode(v) for v in field_value
                                    ]
                                except (RealmDecodingError, InputValidationError):
                                    continue
                                break
                            else:
                                continue
                        else:
                            continue
                    else:
                        raise RealmDecodingError(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is list:
                    list_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )
                    if is_value_ish_type(list_item_type):
                        list_item_decoder2: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            list_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = [
                            list_item_decoder2.decode(v) for v in field_value
                        ]
                    elif get_origin(list_item_type) is not None:
                        list_item_type_origin = get_origin(list_item_type)
                        if list_item_type_origin is typing.Union or (
                            isinstance(list_item_type_origin, type)
                            and issubclass(list_item_type_origin, types.UnionType)
                        ):
                            union_field_result = []
                            for field_item in field_value:
                                list_item_type_args = get_args(list_item_type)
                                for list_item_type_arg in list_item_type_args:
                                    list_subitem_decoder = (
                                        self._realm_codec_registry.get_decoder(
                                            list_item_type_arg, DatabaseRealm
                                        )
                                    )
                                    try:
                                        union_field_result.append(
                                            list_subitem_decoder.decode(field_item)
                                        )
                                        break
                                    except (RealmDecodingError, InputValidationError):
                                        pass
                                else:
                                    raise RealmDecodingError(
                                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                                    )
                            ctor_args[field.name] = union_field_result
                        else:
                            raise Exception(
                                f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                            )
                elif field_type_origin is set:
                    set_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = set()
                    else:
                        set_item_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            set_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = set(
                            set_item_decoder.decode(v) for v in field_value
                        )
                elif field_type_origin is dict:
                    dict_key_type = cast(type[Thing], get_args(field.type)[0])
                    dict_value_type = cast(type[Thing], get_args(field.type)[1])
                    if not isinstance(field_value, dict):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a dict"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = {}
                    else:
                        dict_key_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_key_type, DatabaseRealm
                        )
                        dict_value_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_value_type, DatabaseRealm
                        )
                        ctor_args[field.name] = {
                            dict_key_decoder.decode(k): dict_value_decoder.decode(v)
                            for k, v in field_value.items()
                        }
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

    def encode(self, value: _RecordT) -> RealmThing:
        """Encode a record."""
        result: dict[str, RealmThing] = {}
        all_fields = dataclasses.fields(value)
        for field in all_fields:
            field_value = getattr(value, field.name)

            if is_value_ish(field_value):
                result[field.name] = self._realm_codec_registry.get_encoder(
                    field_value.__class__, DatabaseRealm
                ).encode(field_value)
            elif isinstance(field_value, ParentLink):
                result[field.name + "_ref_id"] = field_value.as_int()
            elif isinstance(field_value, (list, set)):
                if len(field_value) == 0:
                    result[field.name] = []
                else:
                    first_value = next(iter(field_value))
                    if not is_value_ish(first_value):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    list_item_encoder = self._realm_codec_registry.get_encoder(
                        first_value.__class__, DatabaseRealm
                    )
                    result[field.name] = [
                        list_item_encoder.encode(v) for v in field_value
                    ]
            elif isinstance(field_value, dict):
                if len(field_value) == 0:
                    result[field.name] = {}
                else:
                    first_key, first_value = next(iter(field_value.items()))
                    if not is_value_ish(first_key):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )
                    if not is_value_ish(first_value):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )

                    dict_key_encoder = self._realm_codec_registry.get_encoder(
                        first_key.__class__, DatabaseRealm
                    )
                    dict_value_encoder = self._realm_codec_registry.get_encoder(
                        first_value.__class__, DatabaseRealm
                    )

                    encoded_dict_key = dict_key_encoder.encode(first_key)

                    if not isinstance(encoded_dict_key, str):
                        raise Exception(
                            f"Could not encode field {field.name} of type {field.type} for value {value.__class__.__name__}"
                        )

                    result[field.name] = {
                        k: dict_value_encoder.encode(v) for k, v in field_value.items()
                    }
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

    def decode(self, value: RealmThing) -> _RecordT:
        if not isinstance(value, dict):
            raise RealmDecodingError("Expected value to be a dictionary object")

        all_fields = dataclasses.fields(self._the_type)

        ctor_args: dict[
            str, ParentLink | Thing | list[Thing] | set[Thing] | dict[Thing, Thing]
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

            if is_value_ish_type(field.type):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif field.type is ParentLink:
                ctor_args[field.name] = ParentLink(
                    entity_id_decoder.decode(field_value)
                )
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    if len(field_args) == 2 and (
                        (
                            field_args[0] is type(None)
                            and field_args[1] is not type(None)
                        )
                        or (
                            field_args[1] is type(None)
                            and field_args[0] is not type(None)
                        )
                    ):
                        if field_value is None:
                            ctor_args[field.name] = None
                        else:
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_args[0]
                                if field_args[1] is type(None)
                                else field_args[1],
                                DatabaseRealm,
                            )
                            ctor_args[field.name] = field_decoder.decode(field_value)
                    else:
                        raise Exception("Not implemented - union")
                elif field_type_origin is list:
                    list_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = []
                    else:
                        list_item_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            list_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = [
                            list_item_decoder.decode(v) for v in field_value
                        ]
                elif field_type_origin is set:
                    set_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = set()
                    else:
                        set_item_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            set_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = set(
                            set_item_decoder.decode(v) for v in field_value
                        )
                elif field_type_origin is dict:
                    dict_key_type = cast(type[Thing], get_args(field.type)[0])
                    dict_value_type = cast(type[Thing], get_args(field.type)[1])
                    if not isinstance(field_value, dict):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a dict"
                        )
                    if len(field_value) == 0:
                        ctor_args[field.name] = {}
                    else:
                        dict_key_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_key_type, DatabaseRealm
                        )
                        dict_value_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            dict_value_type, DatabaseRealm
                        )
                        ctor_args[field.name] = {
                            dict_key_decoder.decode(k): dict_value_decoder.decode(v)
                            for k, v in field_value.items()
                        }
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

        ctor_args: dict[
            str,
            ParentLink
            | Thing
            | list[Thing]
            | set[Thing]
            | dict[Thing, Thing]
            | UpdateAction[Thing]
            | UpdateAction[list[Thing]],
        ] = {}

        for field in all_fields:
            if field.name not in value:
                raise RealmDecodingError(
                    f"Expected value of type {self._the_type.__name__} to have field {field.name}"
                )

            field_value = value[field.name]

            if is_value_ish_type(field.type):
                ctor_args[field.name] = self._realm_codec_registry.get_decoder(
                    field.type, DatabaseRealm
                ).decode(field_value)
            elif get_origin(field.type) is not None:
                field_type_origin = get_origin(field.type)
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    field_args = get_args(field.type)
                    for field_arg in field_args:
                        if is_value_ish_type(field_arg):
                            field_decoder = self._realm_codec_registry.get_decoder(
                                field_arg, DatabaseRealm
                            )
                            try:
                                ctor_args[field.name] = field_decoder.decode(
                                    field_value
                                )
                                break
                            except (RealmDecodingError, InputValidationError):
                                pass
                        elif get_origin(field_arg) is not None:
                            field_arg_origin = get_origin(field_arg)

                            if field_arg_origin is list:
                                list_item_type = cast(
                                    type[Thing], get_args(field_arg)[0]
                                )
                                if not isinstance(field_value, list):
                                    continue
                                list_item_decoder = (
                                    self._realm_codec_registry.get_decoder(
                                        list_item_type, DatabaseRealm
                                    )
                                )
                                try:
                                    ctor_args[field.name] = [
                                        list_item_decoder.decode(v) for v in field_value
                                    ]
                                except (RealmDecodingError, InputValidationError):
                                    continue
                                break
                            else:
                                continue
                        else:
                            continue
                    else:
                        raise RealmDecodingError(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is UpdateAction:
                    update_action_type = cast(type[Thing], get_args(field.type)[0])
                    if is_value_ish_type(update_action_type):
                        update_action_decoder: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            update_action_type, DatabaseRealm
                        )

                        if field_value is None:
                            ctor_args[field.name] = UpdateAction.do_nothing()
                        else:
                            ctor_args[field.name] = UpdateAction.change_to(
                                update_action_decoder.decode(field_value)
                            )
                    elif get_origin(update_action_type) is not None:
                        update_action_origin_type = get_origin(update_action_type)
                        if update_action_origin_type is typing.Union or (
                            isinstance(update_action_origin_type, type)
                            and issubclass(update_action_origin_type, types.UnionType)
                        ):
                            field_args = get_args(update_action_type)
                            if (
                                f"clear_{field.name}" in value
                                and value[f"clear_{field.name}"] is True
                            ):
                                ctor_args[field.name] = UpdateAction.change_to(None)  # type: ignore
                            elif field_value is None:
                                ctor_args[field.name] = UpdateAction.do_nothing()
                            else:
                                for field_arg in field_args:
                                    field_decoder = (
                                        self._realm_codec_registry.get_decoder(
                                            field_arg, DatabaseRealm
                                        )
                                    )
                                    try:
                                        ctor_args[field.name] = UpdateAction.change_to(  # type: ignore
                                            field_decoder.decode(field_value)
                                        )
                                        break
                                    except (RealmDecodingError, InputValidationError):
                                        pass
                                else:
                                    raise RealmDecodingError(
                                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                                    )
                        elif update_action_origin_type is list:
                            list_item_type = cast(
                                type[Thing], get_args(update_action_type)[0]
                            )
                            if field_value is None:
                                ctor_args[field.name] = UpdateAction.do_nothing()
                            if not isinstance(field_value, list):
                                raise RealmDecodingError(
                                    f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                                )
                            update_list_item_decoder: RealmDecoder[
                                Thing, DatabaseRealm
                            ] = self._realm_codec_registry.get_decoder(
                                list_item_type, DatabaseRealm
                            )
                            partial_result = UpdateAction.change_to(
                                [
                                    update_list_item_decoder.decode(v)
                                    for v in field_value
                                ]
                            )
                            ctor_args[field.name] = partial_result
                        else:
                            raise Exception(
                                f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                            )
                    else:
                        raise Exception(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is list:
                    list_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )

                    if is_value_ish_type(list_item_type):
                        list_item_decoder2: RealmDecoder[
                            Thing, DatabaseRealm
                        ] = self._realm_codec_registry.get_decoder(
                            list_item_type, DatabaseRealm
                        )
                        ctor_args[field.name] = [
                            list_item_decoder2.decode(v) for v in field_value
                        ]
                    elif get_origin(list_item_type) is not None:
                        list_item_type_origin = get_origin(list_item_type)
                        if list_item_type_origin is typing.Union or (
                            isinstance(list_item_type_origin, type)
                            and issubclass(list_item_type_origin, types.UnionType)
                        ):
                            field_list_result = []
                            for field_item in field_value:
                                list_item_type_args = get_args(list_item_type)
                                for list_item_type_arg in list_item_type_args:
                                    list_item_decoder = (
                                        self._realm_codec_registry.get_decoder(
                                            list_item_type_arg, DatabaseRealm
                                        )
                                    )
                                    try:
                                        field_list_result.append(
                                            list_item_decoder.decode(field_item)
                                        )
                                        break
                                    except (RealmDecodingError, InputValidationError):
                                        pass
                                else:
                                    raise RealmDecodingError(
                                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                                    )
                            ctor_args[field.name] = field_list_result
                        else:
                            raise Exception(
                                f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                            )
                    else:
                        raise Exception(
                            f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                        )
                elif field_type_origin is set:
                    set_item_type = cast(type[Thing], get_args(field.type)[0])
                    if not isinstance(field_value, list):
                        raise RealmDecodingError(
                            f"Expected value of type {self._the_type.__name__} to have field {field.name} to be a list"
                        )
                    set_item_decoder: RealmDecoder[
                        Thing, DatabaseRealm
                    ] = self._realm_codec_registry.get_decoder(
                        set_item_type, DatabaseRealm
                    )
                    ctor_args[field.name] = set(
                        set_item_decoder.decode(v) for v in field_value
                    )
                else:
                    raise Exception(
                        f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                    )
            else:
                raise Exception(
                    f"Could not decode field {field.name} of type {field.type} for value {self._the_type.__name__}"
                )

        return self._the_type(**ctor_args)


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
        ) -> Iterator[type[AtomicValue]]:
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
        registry._add_decoder(EntityId, DatabaseRealm, EntityIdDatabaseDecoder())

        registry._add_encoder(
            EntityName, DatabaseRealm, EntityNameDatabaseEncoder(EntityName)
        )
        registry._add_decoder(
            EntityName, DatabaseRealm, EntityNameDatabaseDecoder(EntityName)
        )

        registry._add_encoder(Timestamp, DatabaseRealm, TimestampDatabaseEncoder())
        registry._add_decoder(Timestamp, DatabaseRealm, TimestampDatabaseDecoder())

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

            for use_case_args in extract_use_case_args(m):
                if not registry._has_decoder(use_case_args, CliRealm):
                    registry._add_decoder(
                        use_case_args,
                        CliRealm,
                        _StandardUseCaseArgsCliDecoder(registry, use_case_args),
                    )

        return registry

    def get_encoder(
        self,
        thing_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> RealmEncoder[_ThingT, _RealmT]:
        """Get a codec for a realm and a thing type."""
        if (thing_type, realm) not in self._encoders_registry:
            raise Exception(
                f"Could not find encoder for realm {realm} and thing {thing_type.__name__}"
            )
        return cast(
            RealmEncoder[_ThingT, _RealmT],
            self._encoders_registry[
                cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
            ],
        )

    def get_decoder(
        self,
        thing_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> RealmDecoder[_ThingT, _RealmT]:
        """Get a codec for a realm and a thing type."""
        if (thing_type, realm) not in self._decoders_registry:
            raise Exception(
                f"Could not find decoder for realm {realm} and thing {thing_type.__name__}"
            )
        return cast(
            RealmDecoder[_ThingT, _RealmT],
            self._decoders_registry[
                cast(tuple[type[Thing], type[Realm]], (thing_type, realm))
            ],
        )

    def _has_encoder(
        self,
        thing_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a thing type."""
        return (thing_type, realm) in self._encoders_registry

    def _add_encoder(
        self,
        thing_type: type[_ThingT],
        realm: type[_RealmT],
        encoder: RealmEncoder[_ThingT, _RealmT],
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
        thing_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> bool:
        """Get a codec for a realm and a thing type."""
        return (thing_type, realm) in self._decoders_registry

    def _add_decoder(
        self,
        thing_type: type[_ThingT],
        realm: type[_RealmT],
        decoder: RealmDecoder[_ThingT, _RealmT],
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
