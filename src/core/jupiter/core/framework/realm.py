"""A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""
import abc
from typing import Generic, Mapping, TypeVar

from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.thing import Thing


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

RealmThing = Primitive | list["RealmThing"] | Mapping[str, "RealmThing"]

_ThingT = TypeVar("_ThingT", bound=Thing)
_RealmT = TypeVar("_RealmT", bound=Realm)


class RealmDecodingError(Exception):
    """Error raised when a concept from a realm cannot be decoded to the domain model."""


class RealmEncoder(Generic[_ThingT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def encode(self, value: _ThingT) -> RealmThing:
        """Encode a domain thing to a realm."""


class RealmDecoder(Generic[_ThingT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def decode(self, value: RealmThing) -> _ThingT:
        """Decode a domain thing from realm thing."""


class RealmCodecRegistry(abc.ABC):
    """A registry for realm codecs."""

    @abc.abstractmethod
    def get_encoder(
        self,
        concept_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> RealmEncoder[_ThingT, _RealmT]:
        """Get an encoder for a realm and a concept type."""

    @abc.abstractmethod
    def get_decoder(
        self,
        concept_type: type[_ThingT],
        realm: type[_RealmT],
    ) -> RealmDecoder[_ThingT, _RealmT]:
        """Get a decoder for a realm and a concept type."""
