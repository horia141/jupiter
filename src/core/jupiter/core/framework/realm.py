"""A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""
import abc
from typing import Generic, Mapping, TypeVar

from jupiter.core.framework.concept import Concept
from jupiter.core.framework.primitive import Primitive


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

RealmConcept = Primitive | list["RealmConcept"] | Mapping[str, "RealmConcept"]

_ConceptT = TypeVar("_ConceptT", bound=Concept)
_RealmT = TypeVar("_RealmT", bound=Realm)


class RealmDecodingError(Exception):
    """Error raised when a concept from a realm cannot be decoded to a domain model."""


class RealmEncoder(Generic[_ConceptT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def encode(self, value: _ConceptT) -> RealmConcept:
        """Encode a realm to a string."""


class RealmDecoder(Generic[_ConceptT, _RealmT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def decode(self, value: RealmConcept) -> _ConceptT:
        """Decode a realm from a string."""


class RealmCodecRegistry(abc.ABC):
    """A registry for realm codecs."""

    @abc.abstractmethod
    def get_encoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmEncoder[_ConceptT, _RealmT]:
        """Get an encoder for a realm and a concept type."""

    @abc.abstractmethod
    def get_decoder(
        self,
        concept_type: type[_ConceptT],
        realm: type[_RealmT],
    ) -> RealmDecoder[_ConceptT, _RealmT]:
        """Get a decoder for a realm and a concept type."""
