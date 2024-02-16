"""A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""
import abc
from typing import Callable, ForwardRef, Generic, Iterator, Mapping, TypeVar, Union

from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction


class Realm:
    """A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""


class DatabaseRealm(Realm):
    """The concept is stored in a database and is validated to be correct."""


class EventStoreRealm(Realm):
    """The concept in an event store and is validated to be correct."""


class SearchRealm(Realm):
    """The concept is stored in a search index and is validated to be correct."""


class WebRealm(Realm):
    """The concept comes from the web app and is not validated to be correct."""


class CliRealm(Realm):
    """The concept comes from the CLI app and is not validated to be correct."""


class EmailRealm(Realm):
    """The concept comes from an email (an email task) and is not validated to be correct."""


AllRealms = DatabaseRealm | SearchRealm | WebRealm | CliRealm | EmailRealm

DomainThing = (
    Thing
    | UpdateAction["DomainThing"]
    | Union[Thing, Thing]
    | Union[Thing, Thing, Thing]
    | Union[Thing, Thing, Thing, Thing]
    | list["DomainThing"]
    | set["DomainThing"]
    | dict["DomainThing", "DomainThing"]
)
RealmThing = Primitive | list["RealmThing"] | Mapping[str, "RealmThing"]

_DomainThingT = TypeVar("_DomainThingT", bound=DomainThing)
_RealmT = TypeVar("_RealmT", bound=Realm)


class RealmDecodingError(Exception):
    """Error raised when a concept from a realm cannot be decoded to the domain model."""


class RealmEncoder(Generic[_DomainThingT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def encode(self, value: _DomainThingT) -> RealmThing:
        """Encode a domain thing to a realm."""


class RealmDecoder(Generic[_DomainThingT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def decode(self, value: RealmThing) -> _DomainThingT:
        """Decode a domain thing from realm thing."""


class RealmCodecRegistry(abc.ABC):
    """A registry for realm codecs."""

    @abc.abstractmethod
    def get_all_registered_types(
        self, base_type: type[_DomainThingT], realm: type[Realm]
    ) -> Iterator[type[_DomainThingT]]:
        """Get all types registered that derive from base type."""

    @abc.abstractmethod
    def get_encoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmEncoder[_DomainThingT, _RealmT]:
        """Get an encoder for a realm and a concept type."""

    @abc.abstractmethod
    def get_decoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmDecoder[_DomainThingT, _RealmT]:
        """Get a decoder for a realm and a concept type."""

    def db_encode(
        self, domain_thing: _DomainThingT, realm: type[Realm] = DatabaseRealm
    ) -> RealmThing:
        """Encode a value to the database realm."""
        encoder = self.get_encoder(domain_thing.__class__, realm)
        return encoder.encode(domain_thing)

    def db_decode(
        self,
        domain_thing_type: type[_DomainThingT],
        realm_thing: RealmThing,
        realm: type[Realm] = DatabaseRealm,
    ) -> _DomainThingT:
        """Decode a value from the database realm."""
        decoder = self.get_decoder(domain_thing_type, realm)
        return decoder.decode(realm_thing)


class PlaceholderRealmCodecRegistry(RealmCodecRegistry):
    """A registry for realm codecs."""

    def get_all_registered_types(
        self, base_type: type[_DomainThingT], realm: type[Realm]
    ) -> Iterator[type[_DomainThingT]]:
        """Get all types registered that derive from base type."""
        raise NotImplementedError

    def get_encoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmEncoder[_DomainThingT, _RealmT]:
        """Get an encoder for a realm and a concept type."""
        raise NotImplementedError

    def get_decoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmDecoder[_DomainThingT, _RealmT]:
        """Get a decoder for a realm and a concept type."""
        raise NotImplementedError


PROVIDE_VIA_REGISTRY = PlaceholderRealmCodecRegistry()

_ThingT = TypeVar("_ThingT", bound=Thing)


def only_in_realm(*realms: type[Realm]) -> Callable[[type[_ThingT]], type[_ThingT]]:
    def decorator(cls: type[_ThingT]) -> type[_ThingT]:
        setattr(cls, "__allowed_realms", list(realms))
        return cls

    return decorator


def allowed_in_realm(cls: type[_ThingT], realm: type[Realm]) -> bool:
    """Check that a particular concep can be represented in a given realm."""
    if not hasattr(cls, "__allowed_realms"):
        return True

    allowed_realms = getattr(cls, "__allowed_realms")

    if not isinstance(allowed_realms, list):
        raise Exception("Invalid realms check")

    return realm in allowed_realms
