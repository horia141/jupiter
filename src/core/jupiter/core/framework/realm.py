"""A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""
import abc
from typing import ForwardRef, Generic, Iterator, Mapping, TypeVar, Union

from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.thing import Thing
from jupiter.core.framework.update_action import UpdateAction


class Realm:
    """A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""


class DatabaseRealm(Realm):
    """The concept is stored in a database and is validated to be correct."""


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
    def get_all_registered_types(self, base_type: type[Thing], realm: type[Realm]) -> Iterator[type[Thing]]:
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


class PlaceholderRealmCodecRegistry(RealmCodecRegistry):
    """A registry for realm codecs."""

    def get_all_registered_types(self, base_type: type[Thing], realm: type[Realm]) -> Iterator[type[Thing]]:
        """Get all types registered that derive from base type."""
        raise NotImplementedError()

    def get_encoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmEncoder[_DomainThingT, _RealmT]:
        """Get an encoder for a realm and a concept type."""
        raise NotImplementedError()

    def get_decoder(
        self,
        concept_type: type[_DomainThingT] | ForwardRef | str,
        realm: type[_RealmT],
        root_type: type[DomainThing] | None = None,
    ) -> RealmDecoder[_DomainThingT, _RealmT]:
        """Get a decoder for a realm and a concept type."""
        raise NotImplementedError()


PROVIDE_VIA_REGISTRY = PlaceholderRealmCodecRegistry()
