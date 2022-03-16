"""Framework level elements for storage."""
import abc
from typing import Generic, TypeVar, Optional, Iterable, List

from jupiter.domain.entity_key import EntityKey
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.entity import RootEntity, TrunkEntity, StubEntity, BranchEntity, LeafEntity, Entity


class Repository(abc.ABC):
    """A repository."""


class EntityAlreadyExistsError(Exception):
    """Error raised when an entity already exists."""


class EntityNotFoundError(Exception):
    """Error raised when an entity is not found."""


EntityType = TypeVar("EntityType", bound=Entity)


class EntityRepository(Generic[EntityType], Repository, abc.ABC):
    """A repository for entities."""

    @abc.abstractmethod
    def create(self, entity: EntityType) -> EntityType:
        """Create an entity."""

    @abc.abstractmethod
    def save(self, entity: EntityType) -> EntityType:
        """Save an entity."""


class RootEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a root entity already exists."""


class RootEntityNotFoundError(EntityNotFoundError):
    """Error raised when a root entity is not found."""


RootEntityType = TypeVar("RootEntityType", bound=RootEntity)


class RootEntityRepository(EntityRepository[RootEntityType], abc.ABC):
    """A repository for root entities."""

    @abc.abstractmethod
    def load(self) -> RootEntityType:
        """Loads the root entity."""

    @abc.abstractmethod
    def load_optional(self) -> Optional[RootEntityType]:
        """Loads the root entity but returns null if there isn't one."""


class TrunkEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a trunk entity already exists."""


class TrunkEntityNotFoundError(EntityNotFoundError):
    """Error raised when a trunk entity is not found."""


TrunkEntityType = TypeVar("TrunkEntityType", bound=TrunkEntity)


class TrunkEntityRepository(EntityRepository[TrunkEntityType], abc.ABC):
    """A repository for trunk entities."""

    @abc.abstractmethod
    def load_by_parent(self, parent_ref_id: EntityId) -> TrunkEntityType:
        """Retrieve a trunk by its owning parent id."""


class StubEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a stub entity with the given key already exists."""


class StubEntityNotFoundError(EntityNotFoundError):
    """Error raised when a stub entity is not found."""


StubEntityType = TypeVar("StubEntityType", bound=StubEntity)


class StubEntityRepository(EntityRepository[StubEntityType], abc.ABC):
    """A repository for stub entities."""

    @abc.abstractmethod
    def load_by_parent(self, parent_ref_id: EntityId) -> StubEntityType:
        """Retrieve a stub by its owning parent id."""


class BranchEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a branch entity with the given key already exists."""


class BranchEntityNotFoundError(EntityNotFoundError):
    """Error raised when a branch entity is not found."""


BranchEntityKeyType = TypeVar("BranchEntityKeyType", bound=EntityKey)
BranchEntityType = TypeVar("BranchEntityType", bound=BranchEntity)


class BranchEntityRepository(
        Generic[BranchEntityKeyType, BranchEntityType], EntityRepository[BranchEntityType], abc.ABC):
    """A repository for branch entities."""

    @abc.abstractmethod
    def load_by_key(self, parent_ref_id: EntityId, key: BranchEntityKeyType) -> BranchEntityType:
        """Find a branch by key."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BranchEntityType:
        """Find a branch by id."""

    @abc.abstractmethod
    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[BranchEntityKeyType]] = None) -> List[BranchEntityType]:
        """Find all branches matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> BranchEntityType:
        """Hard remove a branch - an irreversible operation."""


class LeafEntityNotFoundError(EntityNotFoundError):
    """Error raised when a leaf entity is not found."""


LeafEntityType = TypeVar("LeafEntityType", bound=LeafEntity)


class LeafEntityRepository(EntityRepository[LeafEntityType], abc.ABC):
    """A repository for leaf entities."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> LeafEntityType:
        """Load a leaf by id."""

    @abc.abstractmethod
    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[LeafEntityType]:
        """Find all leaves."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> LeafEntityType:
        """Hard remove a leaf - an irreversible operation."""
