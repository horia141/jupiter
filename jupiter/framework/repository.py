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


EntityT = TypeVar("EntityT", bound=Entity)


class EntityRepository(Generic[EntityT], Repository, abc.ABC):
    """A repository for entities."""

    @abc.abstractmethod
    def create(self, entity: EntityT) -> EntityT:
        """Create an entity."""

    @abc.abstractmethod
    def save(self, entity: EntityT) -> EntityT:
        """Save an entity."""


class RootEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a root entity already exists."""


class RootEntityNotFoundError(EntityNotFoundError):
    """Error raised when a root entity is not found."""


RootEntityT = TypeVar("RootEntityT", bound=RootEntity)


class RootEntityRepository(EntityRepository[RootEntityT], abc.ABC):
    """A repository for root entities."""

    @abc.abstractmethod
    def load(self) -> RootEntityT:
        """Loads the root entity."""

    @abc.abstractmethod
    def load_optional(self) -> Optional[RootEntityT]:
        """Loads the root entity but returns null if there isn't one."""


class TrunkEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a trunk entity already exists."""


class TrunkEntityNotFoundError(EntityNotFoundError):
    """Error raised when a trunk entity is not found."""


TrunkEntityT = TypeVar("TrunkEntityT", bound=TrunkEntity)


class TrunkEntityRepository(EntityRepository[TrunkEntityT], abc.ABC):
    """A repository for trunk entities."""

    @abc.abstractmethod
    def load_by_parent(self, parent_ref_id: EntityId) -> TrunkEntityT:
        """Retrieve a trunk by its owning parent id."""


class StubEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a stub entity with the given key already exists."""


class StubEntityNotFoundError(EntityNotFoundError):
    """Error raised when a stub entity is not found."""


StubEntityT = TypeVar("StubEntityT", bound=StubEntity)


class StubEntityRepository(EntityRepository[StubEntityT], abc.ABC):
    """A repository for stub entities."""

    @abc.abstractmethod
    def load_by_parent(self, parent_ref_id: EntityId) -> StubEntityT:
        """Retrieve a stub by its owning parent id."""


class BranchEntityAlreadyExistsError(EntityAlreadyExistsError):
    """Error raised when a branch entity with the given key already exists."""


class BranchEntityNotFoundError(EntityNotFoundError):
    """Error raised when a branch entity is not found."""


BranchEntityKeyT = TypeVar("BranchEntityKeyT", bound=EntityKey)
BranchEntityT = TypeVar("BranchEntityT", bound=BranchEntity)


class BranchEntityRepository(
        Generic[BranchEntityKeyT, BranchEntityT], EntityRepository[BranchEntityT], abc.ABC):
    """A repository for branch entities."""

    @abc.abstractmethod
    def load_by_key(self, parent_ref_id: EntityId, key: BranchEntityKeyT) -> BranchEntityT:
        """Find a branch by key."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> BranchEntityT:
        """Find a branch by id."""

    @abc.abstractmethod
    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_keys: Optional[Iterable[BranchEntityKeyT]] = None) -> List[BranchEntityT]:
        """Find all branches matching some criteria."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> BranchEntityT:
        """Hard remove a branch - an irreversible operation."""


class LeafEntityNotFoundError(EntityNotFoundError):
    """Error raised when a leaf entity is not found."""


LeafEntityT = TypeVar("LeafEntityT", bound=LeafEntity)


class LeafEntityRepository(EntityRepository[LeafEntityT], abc.ABC):
    """A repository for leaf entities."""

    @abc.abstractmethod
    def load_by_id(self, ref_id: EntityId, allow_archived: bool = False) -> LeafEntityT:
        """Load a leaf by id."""

    @abc.abstractmethod
    def find_all(
            self,
            parent_ref_id: EntityId,
            allow_archived: bool = False,
            filter_ref_ids: Optional[Iterable[EntityId]] = None) -> List[LeafEntityT]:
        """Find all leaves."""

    @abc.abstractmethod
    def remove(self, ref_id: EntityId) -> LeafEntityT:
        """Hard remove a leaf - an irreversible operation."""
