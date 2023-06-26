"""Framework level elements for storage."""
import abc
from typing import Generic, Iterable, List, Optional, TypeVar

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import (
    BranchEntity,
    Entity,
    LeafEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)


class Repository:
    """A repository."""


class EntityAlreadyExistsError(Exception):
    """Error raised when an entity already exists."""


class EntityNotFoundError(Exception):
    """Error raised when an entity is not found."""


EntityT = TypeVar("EntityT", bound=Entity)


class EntityRepository(Generic[EntityT], Repository, abc.ABC):
    """A repository for entities."""

    @abc.abstractmethod
    async def create(self, entity: EntityT) -> EntityT:
        """Create an entity."""

    @abc.abstractmethod
    async def save(self, entity: EntityT) -> EntityT:
        """Save an entity."""


class RootEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a root entity already exists."""


class RootEntityNotFoundError(EntityNotFoundError):
    """Error raised when a root entity is not found."""


RootEntityT = TypeVar("RootEntityT", bound=RootEntity)


class RootEntityRepository(EntityRepository[RootEntityT], abc.ABC):
    """A repository for root entities."""

    @abc.abstractmethod
    async def load_by_id(self, entity_id: EntityId) -> RootEntityT:
        """Loads the root entity."""

    @abc.abstractmethod
    async def load_optional(self, entity_id: EntityId) -> Optional[RootEntityT]:
        """Loads the root entity but returns null if there isn't one."""


class TrunkEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a trunk entity already exists."""


class TrunkEntityNotFoundError(EntityNotFoundError):
    """Error raised when a trunk entity is not found."""


TrunkEntityT = TypeVar("TrunkEntityT", bound=TrunkEntity)


class TrunkEntityRepository(EntityRepository[TrunkEntityT], abc.ABC):
    """A repository for trunk entities."""

    @abc.abstractmethod
    async def load_by_parent(self, parent_ref_id: EntityId) -> TrunkEntityT:
        """Retrieve a trunk by its owning parent id."""


class StubEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a stub entity with the given key already exists."""


class StubEntityNotFoundError(EntityNotFoundError):
    """Error raised when a stub entity is not found."""


StubEntityT = TypeVar("StubEntityT", bound=StubEntity)


class StubEntityRepository(EntityRepository[StubEntityT], abc.ABC):
    """A repository for stub entities."""

    @abc.abstractmethod
    async def load_by_parent(self, parent_ref_id: EntityId) -> StubEntityT:
        """Retrieve a stub by its owning parent id."""


class BranchEntityNotFoundError(EntityNotFoundError):
    """Error raised when a branch entity is not found."""


BranchEntityT = TypeVar("BranchEntityT", bound=BranchEntity)


class BranchEntityRepository(
    Generic[BranchEntityT],
    EntityRepository[BranchEntityT],
    abc.ABC,
):
    """A repository for branch entities."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> BranchEntityT:
        """Find a branch by id."""

    @abc.abstractmethod
    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[BranchEntityT]:
        """Find all branches matching some criteria."""

    @abc.abstractmethod
    async def remove(self, ref_id: EntityId) -> BranchEntityT:
        """Hard remove a branch - an irreversible operation."""


class LeafEntityNotFoundError(EntityNotFoundError):
    """Error raised when a leaf entity is not found."""


LeafEntityT = TypeVar("LeafEntityT", bound=LeafEntity)


class LeafEntityRepository(EntityRepository[LeafEntityT], abc.ABC):
    """A repository for leaf entities."""

    @abc.abstractmethod
    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> LeafEntityT:
        """Load a leaf by id."""

    @abc.abstractmethod
    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[LeafEntityT]:
        """Find all leaves."""

    @abc.abstractmethod
    async def remove(self, ref_id: EntityId) -> LeafEntityT:
        """Hard remove a leaf - an irreversible operation."""