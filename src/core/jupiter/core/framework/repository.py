"""Framework level elements for storage."""
import abc
from typing import Generic, Iterable, List, Optional, TypeVar

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import (
    BranchEntity,
    CrownEntity,
    Entity,
    EntityLinkFilterCompiled,
    LeafEntity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.record import Record


class Repository:
    """A repository."""


RecordT = TypeVar("RecordT", bound=Record)
RecordKeyT = TypeVar("RecordKeyT")
RecordKeyPrefixT = TypeVar("RecordKeyPrefixT")


class RecordAlreadyExistsError(Exception):
    """Error raised when a record already exists."""


class RecordNotFoundError(Exception):
    """Error raised when a record is not found."""


class RecordRepository(
    Generic[RecordT, RecordKeyT, RecordKeyPrefixT], Repository, abc.ABC
):
    """A repository for records."""

    @abc.abstractmethod
    async def create(self, record: RecordT) -> RecordT:
        """Create a record."""

    @abc.abstractmethod
    async def save(self, record: RecordT) -> RecordT:
        """Save a record."""

    @abc.abstractmethod
    async def remove(self, key: RecordKeyT) -> RecordT:
        """Hard remove a record - an irreversible operation."""

    @abc.abstractmethod
    async def load_by_key_optional(self, key: RecordKeyT) -> RecordT | None:
        """Load a record by it's unique key."""

    @abc.abstractmethod
    async def find_all(self, prefix: RecordKeyPrefixT) -> List[RecordT]:
        """Find all records matching some criteria."""


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


RootEntityT = TypeVar("RootEntityT", bound=RootEntity)


class RootEntityRepository(EntityRepository[RootEntityT], abc.ABC):
    """A repository for root entities."""

    @abc.abstractmethod
    async def load_by_id(self, entity_id: EntityId) -> RootEntityT:
        """Loads the root entity."""

    @abc.abstractmethod
    async def load_optional(self, entity_id: EntityId) -> Optional[RootEntityT]:
        """Loads the root entity but returns null if there isn't one."""

    @abc.abstractmethod
    async def find_all(
        self,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[RootEntityT]:
        """Find all root entities matching some criteria."""


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

    @abc.abstractmethod
    async def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> TrunkEntityT:
        """Retrieve a trunk by its id."""


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


CrownEntityT = TypeVar("CrownEntityT", bound=CrownEntity)


class CrownEntityRepository(EntityRepository[CrownEntityT], abc.ABC):
    """A repository for crown entities."""

    @abc.abstractmethod
    async def load_by_id(
        self, ref_id: EntityId, allow_archived: bool = False
    ) -> CrownEntityT:
        """Retrieve a crown by its id."""

    @abc.abstractmethod
    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> List[CrownEntityT]:
        """Find all crowns matching some criteria."""

    @abc.abstractmethod
    async def find_all_generic(
        self,
        *,
        parent_ref_id: EntityId | None = None,
        allow_archived: bool = False,
        **kwargs: EntityLinkFilterCompiled,
    ) -> list[CrownEntityT]:
        """Find all crowns with generic filters."""

    @abc.abstractmethod
    async def remove(self, ref_id: EntityId) -> CrownEntityT:
        """Hard remove a crown - an irreversible operation."""


BranchEntityT = TypeVar("BranchEntityT", bound=BranchEntity)


class BranchEntityRepository(
    Generic[BranchEntityT],
    CrownEntityRepository[BranchEntityT],
    abc.ABC,
):
    """A repository for branch entities."""


LeafEntityT = TypeVar("LeafEntityT", bound=LeafEntity)


class LeafEntityRepository(
    Generic[LeafEntityT], CrownEntityRepository[LeafEntityT], abc.ABC
):
    """A repository for leaf entities."""
