"""Domain-level storage interaction."""
import abc
from typing import AsyncContextManager, Type, TypeVar, overload

from jupiter.core.domain.search.infra.search_repository import SearchRepository
from jupiter.core.framework.entity import (
    CrownEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.repository import (
    CrownEntityRepository,
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


class DomainUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @abc.abstractmethod
    def get(self, repository: type[_RepositoryT]) -> _RepositoryT:
        """Retrieve a repository"""

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: Type[_RootEntityT]
    ) -> RootEntityRepository[_RootEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: Type[_StubEntityT]
    ) -> StubEntityRepository[_StubEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: Type[_TrunkEntityT]
    ) -> TrunkEntityRepository[_TrunkEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def get_for(
        self, entity_type: Type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository."""

    @abc.abstractmethod
    def get_for(
        self,
        entity_type: Type[_RootEntityT]
        | Type[_StubEntityT]
        | Type[_TrunkEntityT]
        | Type[_CrownEntityT],
    ) -> RootEntityRepository[_RootEntityT] | StubEntityRepository[
        _StubEntityT
    ] | TrunkEntityRepository[_TrunkEntityT] | CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository."""


class DomainStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AsyncContextManager[DomainUnitOfWork]:
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
    def get_unit_of_work(self) -> AsyncContextManager[SearchUnitOfWork]:
        """Build a unit of work."""
