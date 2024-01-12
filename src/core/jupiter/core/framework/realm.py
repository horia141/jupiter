"""A realm denotes the storage existance and validation correctness of a particular Jupiter concept (value, record, entity)."""

import abc
from typing import Generic, TypeVar

from jupiter.core.framework.concept import Concept


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

RealmConcept = None | bool | int | float | str | list["RealmConcept"] | dict[str, "RealmConcept"]

_ConceptT = TypeVar("_ConceptT", bound=Concept)
_RealmT = TypeVar("_RealmT", bound=Realm)

class RealmDecodingError(Exception):
    """Error raised when a concept from a realm cannot be decoded to a domain model."""


class RealmEncoder(Generic[_RealmT, _ConceptT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def encode(self, value: _ConceptT) -> RealmConcept:
        """Encode a realm to a string."""


class RealmDecoder(Generic[_RealmT, _ConceptT], abc.ABC):
    """A encoder and decoder for a realm and a particular type."""

    @abc.abstractmethod
    def decode(self, value: RealmConcept) -> _ConceptT:
        """Decode a realm from a string."""


class RealmCodecRegistry(abc.ABC):
    """A registry for realm codecs."""

    @abc.abstractmethod
    def get_encoder(
        self, realm: type[_RealmT], concept_type: type[_ConceptT]
    ) -> RealmEncoder[_RealmT, _ConceptT]:
        """Get an encoder for a realm and a concept type."""

    @abc.abstractmethod
    def get_decoder(
        self, realm: type[_RealmT], concept_type: type[_ConceptT]
    ) -> RealmDecoder[_RealmT, _ConceptT]:
        """Get a decoder for a realm and a concept type."""
