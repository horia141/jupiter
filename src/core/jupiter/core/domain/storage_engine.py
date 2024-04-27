"""Domain-level storage interaction."""
import abc
from contextlib import AbstractAsyncContextManager
from typing import TypeVar, overload

from jupiter.core.domain.search.infra.search_repository import SearchRepository
from jupiter.core.framework.entity import (
    CrownEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.record import Record
from jupiter.core.framework.repository import (
    CrownEntityRepository,
    RecordRepository,
    Repository,
    RootEntityRepository,
    StubEntityRepository,
    TrunkEntityRepository,
)

_RepositoryT = TypeVar("_RepositoryT", bound=Repository)
_RootEntityT = TypeVar("_RootEntityT", bound=RootEntity)
_StubEntityT = TypeVar("_StubEntityT", bound=StubEntity)
_TrunkEntityT = TypeVar("_TrunkEntityT", bound=TrunkEntity)
_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)
_RecordT = TypeVar("_RecordT", bound=Record)


class DomainUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @abc.abstractmethod
    def get(self, repository: type[_RepositoryT]) -> _RepositoryT:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: type[_RootEntityT]
    ) -> RootEntityRepository[_RootEntityT]:
        ...

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: type[_StubEntityT]
    ) -> StubEntityRepository[_StubEntityT]:
        ...

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: type[_TrunkEntityT]
    ) -> TrunkEntityRepository[_TrunkEntityT]:
        ...

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        ...

    @abc.abstractmethod
    def get_for(
        self,
        entity_type: type[_RootEntityT]
        | type[_StubEntityT]
        | type[_TrunkEntityT]
        | type[_CrownEntityT],
    ) -> RootEntityRepository[_RootEntityT] | StubEntityRepository[
        _StubEntityT
    ] | TrunkEntityRepository[_TrunkEntityT] | CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository for a specific entity type."""

    @abc.abstractmethod
    def get_for_record(
        self, record_type: type[_RecordT]
    ) -> RecordRepository[_RecordT, object]:
        """Retrieve a repository for a specific record type."""


class DomainStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AbstractAsyncContextManager[DomainUnitOfWork]:
        """Build a unit of work."""


class SearchUnitOfWork(abc.ABC):
    """A unit of work from a search engine."""

    @property
    @abc.abstractmethod
    def search_repository(self) -> SearchRepository:
        """The search repostory."""


class SearchStorageEngine(abc.ABC):
    """A storage engine of some form for the search engine."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AbstractAsyncContextManager[SearchUnitOfWork]:
        """Build a unit of work."""
