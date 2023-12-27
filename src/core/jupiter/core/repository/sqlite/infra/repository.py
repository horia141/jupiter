"""An entity repository with a lot of defaults."""

import abc
from typing import (
    Final,
    Generic,
    Iterable,
    Optional,
    Protocol,
    TypeGuard,
    TypeVar,
    cast,
    get_args,
)

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
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
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    MetaData,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

_EntityT = TypeVar("_EntityT", bound=Entity)


class SqliteEntityRepository(Generic[_EntityT], abc.ABC):
    """A repository for entities backed by SQLite, meant to be used as a mixin."""

    _connection: Final[AsyncConnection]
    _table: Final[Table]
    _event_table: Final[Table]

    def __init__(self, connection: AsyncConnection, metadata: MetaData, table: Table):
        """Initialize the repository."""
        self._connection = connection
        self._table = table
        self._event_table = build_event_table(self._table, metadata)

    async def create(self, entity: _EntityT) -> _EntityT:
        """Create an entity."""
        ref_id_kw = {}
        if entity.ref_id != BAD_REF_ID:
            ref_id_kw["ref_id"] = entity.ref_id.as_int()
        try:
            result = await self._connection.execute(
                insert(self._table).values(**ref_id_kw, **self._entity_to_row(entity)),
            )
        except IntegrityError as err:
            if isinstance(entity, CrownEntity):
                raise EntityAlreadyExistsError(
                    f"Entity of type {self._infer_entity_class()} with name {entity.name} already exists",
                ) from err
            else:
                raise EntityAlreadyExistsError(
                    f"Entity of type {self._infer_entity_class()} already exists",
                ) from err
        entity = entity.assign_ref_id(EntityId(str(result.inserted_primary_key[0])))
        await upsert_events(
            self._connection,
            self._event_table,
            entity,
        )
        return entity

    async def save(self, entity: _EntityT) -> _EntityT:
        """Save an entity."""
        result = await self._connection.execute(
            update(self._table)
            .where(self._table.c.ref_id == entity.ref_id.as_int())
            .values(**self._entity_to_row(entity)),
        )
        if result.rowcount == 0:
            raise EntityNotFoundError(
                f"Entity of type {entity.__class__} and id {str(entity.ref_id)} not found."
            )
        await upsert_events(
            self._connection,
            self._event_table,
            entity,
        )
        return entity

    @staticmethod
    @abc.abstractmethod
    def _entity_to_row(entity: _EntityT) -> RowType:
        """Convert an entity to a row."""

    @staticmethod
    @abc.abstractmethod
    def _row_to_entity(row: RowType) -> _EntityT:
        """Convert a row to an entity."""

    def _infer_entity_class(self) -> type[_EntityT]:
        """Infer the entity class from the table."""
        # We look over all classes we inherit from, and find the one that has a
        # generic parameter.
        if not _is_indirect_generic_subclass(self):
            raise Exception(
                "Could not infer entity class from repository class because inheritance is messed-up"
            )
        for base in self.__class__.__orig_bases__:
            args = get_args(base)
            if len(args) > 0:
                return cast(type[_EntityT], args[0])

        raise Exception(
            "Could not infer entity class from repository class because inheritance is messed-up"
        )


class _GenericAlias(Protocol):
    __origin__: type[object]


class _IndirectGenericSubclass(Protocol):
    __orig_bases__: tuple[_GenericAlias]


def _is_indirect_generic_subclass(
    obj: object,
) -> TypeGuard[_IndirectGenericSubclass]:
    bases = obj.__orig_bases__
    return bases is not None and isinstance(bases, tuple)


_RootEntityT = TypeVar("_RootEntityT", bound=RootEntity)


class SqliteRootEntityRepository(
    Generic[_RootEntityT], SqliteEntityRepository[_RootEntityT], abc.ABC
):
    """A repository for root entities backed by SQLite, meant to be used as a mixin."""

    async def load_by_id(self, entity_id: EntityId) -> _RootEntityT:
        """Loads the root entity."""
        query_stmt = select(self._table).where(
            self._table.c.ref_id == entity_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} and id {str(entity_id)} not found."
            )
        return self._row_to_entity(result)

    async def load_optional(self, entity_id: EntityId) -> Optional[_RootEntityT]:
        """Loads the root entity but returns null if there isn't one."""
        query_stmt = select(self._table).where(
            self._table.c.ref_id == entity_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            return None
        return self._row_to_entity(result)

    async def find_all(
        self,
        allow_archived: bool = False,
        filter_ref_ids: Iterable[EntityId] | None = None,
    ) -> list[_RootEntityT]:
        """Find all entities links matching some criteria."""
        query_stmt = select(self._table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_([ref_id.as_int() for ref_id in filter_ref_ids])
            )

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]


_TrunkEntityT = TypeVar("_TrunkEntityT", bound=TrunkEntity)


class SqliteTrunkEntityRepository(
    Generic[_TrunkEntityT], SqliteEntityRepository[_TrunkEntityT], abc.ABC
):
    """A repository for trunk entities backed by SQLite, meant to be used as a mixin."""

    async def load_by_parent(self, parent_ref_id: EntityId) -> _TrunkEntityT:
        """Loads the trunk entity."""
        query_stmt = select(self._table).where(
            self._table.c[self._get_parent_field_name()] == parent_ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} and parent id {str(parent_ref_id)} not found."
            )
        return self._row_to_entity(result)

    async def load_by_id(
        self, entity_id: EntityId, allow_archived: bool = False
    ) -> _TrunkEntityT:
        """Loads the trunk entity."""
        query_stmt = select(self._table).where(
            self._table.c.ref_id == entity_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} and id {str(entity_id)} not found."
            )
        return self._row_to_entity(result)

    @staticmethod
    @abc.abstractmethod
    def _get_parent_field_name() -> str:
        ...


_StubEntityT = TypeVar("_StubEntityT", bound=StubEntity)


class SqliteStubEntityRepository(
    Generic[_StubEntityT], SqliteEntityRepository[_StubEntityT], abc.ABC
):
    """A repository for stub entities backed by SQLite, meant to be used as a mixin."""

    async def load_by_parent(self, parent_ref_id: EntityId) -> _StubEntityT:
        """Retrieve a stub entity."""
        query_stmt = select(self._table).where(
            self._table.c[self._get_parent_field_name()] == parent_ref_id.as_int()
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} and parent id {str(parent_ref_id)} not found."
            )
        return self._row_to_entity(result)

    @staticmethod
    @abc.abstractmethod
    def _get_parent_field_name() -> str:
        ...


_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)


class SqliteCrownEntityRepository(
    Generic[_CrownEntityT], SqliteEntityRepository[_CrownEntityT], abc.ABC
):
    """A repository for crown entities backed by SQLite, meant to be used as a mixin."""

    async def load_by_id(
        self,
        ref_id: EntityId,
        allow_archived: bool = False,
    ) -> _CrownEntityT:
        """Find a note by id."""
        query_stmt = select(self._table).where(
            self._table.c.ref_id == ref_id.as_int(),
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} identified by {ref_id} does not exist"
            )
        return self._row_to_entity(result)

    async def find_all(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> list[_CrownEntityT]:
        """Find all crowns matching some criteria."""
        query_stmt = select(self._table).where(
            self._table.c[self._get_parent_field_name()] == parent_ref_id.as_int()
        )
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))
        if filter_ref_ids is not None:
            query_stmt = query_stmt.where(
                self._table.c.ref_id.in_([fi.as_int() for fi in filter_ref_ids])
            )
        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[_CrownEntityT]:
        """Find all crowns with generic filters."""
        query_stmt = select(self._table)
        if not allow_archived:
            query_stmt = query_stmt.where(self._table.c.archived.is_(False))

        query_stmt = compile_query_relative_to(query_stmt, self._table, kwargs)

        results = await self._connection.execute(query_stmt)
        return [self._row_to_entity(row) for row in results]

    async def remove(self, ref_id: EntityId) -> _CrownEntityT:
        """Hard remove a crown - an irreversible operation."""
        query_stmt = select(self._table).where(
            self._table.c.ref_id == ref_id.as_int(),
        )
        result = (await self._connection.execute(query_stmt)).first()
        if result is None:
            raise EntityNotFoundError(
                f"Entity of type {self._infer_entity_class()} identified by {ref_id} does not exist"
            )
        await self._connection.execute(
            delete(self._table).where(
                self._table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._event_table, ref_id)
        return self._row_to_entity(result)

    @staticmethod
    @abc.abstractmethod
    def _get_parent_field_name() -> str:
        ...


_BranchEntityT = TypeVar("_BranchEntityT", bound=BranchEntity)


class SqliteBranchEntityRepository(
    Generic[_BranchEntityT], SqliteCrownEntityRepository[_BranchEntityT], abc.ABC
):
    """A repository for branch entities backed by SQLite, meant to be used as a mixin."""


_LeafEntityT = TypeVar("_LeafEntityT", bound=LeafEntity)


class SqliteLeafEntityRepository(
    Generic[_LeafEntityT], SqliteCrownEntityRepository[_LeafEntityT], abc.ABC
):
    """A repository for leaf entities backed by SQLite, meant to be used as a mixin."""
