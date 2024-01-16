"""An entity repository with a lot of defaults."""

import abc
import dataclasses
import types
import typing
from datetime import date, datetime
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
    get_origin,
)

import inflection
import pendulum
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.entity_name import EntityName
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import (
    BranchEntity,
    CrownEntity,
    Entity,
    EntityLinkFilterCompiled,
    LeafEntity,
    ParentLink,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import DatabaseRealm, RealmCodecRegistry
from jupiter.core.framework.repository import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
)
from jupiter.core.repository.sqlite.infra.events import (
    build_event_table,
    remove_events,
    upsert_events,
)
from jupiter.core.repository.sqlite.infra.filters import compile_query_relative_to
from jupiter.core.repository.sqlite.infra.row import RowType
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine.row import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection

_EntityT = TypeVar("_EntityT", bound=Entity)


class SqliteEntityRepository(Generic[_EntityT], abc.ABC):
    """A repository for entities backed by SQLite, meant to be used as a mixin."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _connection: Final[AsyncConnection]
    _table: Final[Table]
    _event_table: Final[Table]
    _entity_type: type[_EntityT]
    _already_exists_err_cls: Final[type[Exception]]
    _not_found_err_cls: Final[type[Exception]]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        table: Table | None = None,
        already_exists_err_cls: type[Exception] = EntityAlreadyExistsError,
        not_found_err_cls: type[Exception] = EntityNotFoundError,
    ):
        """Initialize the repository."""
        entity_type = self._infer_entity_class()
        self._realm_codec_registry = realm_codec_registry
        self._connection = connection
        self._table = (
            table
            if table is not None
            else SqliteEntityRepository._build_table_for_entity(metadata, entity_type)
        )
        self._event_table = build_event_table(self._table, metadata)
        self._entity_type = entity_type
        self._already_exists_err_cls = already_exists_err_cls
        self._not_found_err_cls = not_found_err_cls

    async def create(self, entity: _EntityT) -> _EntityT:
        """Create an entity."""
        if entity.ref_id != BAD_REF_ID:
            raise Exception("Cannot create an entity with a ref_id already set")
        try:
            entity_for_db = self._entity_to_row(entity)
            del entity_for_db["ref_id"]
            result = await self._connection.execute(
                insert(self._table).values(**entity_for_db),
            )
        except IntegrityError as err:
            if isinstance(entity, CrownEntity):
                raise self._already_exists_err_cls(
                    f"Entity of type {self._entity_type.__name__} with name {entity.name} already exists",
                ) from err
            else:
                raise self._already_exists_err_cls(
                    f"Entity of type {self._entity_type.__name__} already exists",
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
        try:
            result = await self._connection.execute(
                update(self._table)
                .where(self._table.c.ref_id == entity.ref_id.as_int())
                .values(**self._entity_to_row(entity)),
            )
        except IntegrityError as err:
            if isinstance(entity, CrownEntity):
                raise self._already_exists_err_cls(
                    f"Entity of type {self._entity_type.__name__} with name {entity.name} already exists",
                ) from err
            else:
                raise self._already_exists_err_cls(
                    f"Entity of type {self._entity_type.__name__} already exists",
                ) from err
        if result.rowcount == 0:
            raise self._not_found_err_cls(
                f"Entity of type {entity.__class__} and id {str(entity.ref_id)} not found."
            )
        await upsert_events(
            self._connection,
            self._event_table,
            entity,
        )
        return entity

    def _entity_to_row(self, entity: _EntityT) -> RowType:
        encoder = self._realm_codec_registry.get_encoder(
            self._entity_type, DatabaseRealm
        )
        return cast(RowType, encoder.encode(entity))

    def _row_to_entity(self, row: Row) -> _EntityT:
        decoder = self._realm_codec_registry.get_decoder(
            self._entity_type, DatabaseRealm
        )
        return decoder.decode(row._mapping)

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

    def _get_parent_field_name(self) -> str:
        all_fields = dataclasses.fields(self._entity_type)
        for field in all_fields:
            if field.type == ParentLink:
                return field.name + "_ref_id"

        raise Exception(
            f"Critical exception, missiong parent field for class {self._entity_type.__name__}"
        )

    @staticmethod
    def _build_table_for_entity(
        metadata: MetaData, entity_type: type[_EntityT]
    ) -> Table:
        """Build the table for an entity."""

        def extract_entity_table_name() -> str:
            return inflection.underscore(entity_type.__name__)

        def extract_field_type(
            field: dataclasses.Field[Primitive | object],
        ) -> tuple[type[object], bool]:
            field_type_origin = get_origin(field.type)
            if field_type_origin is None:
                return field.type, False

            if field_type_origin is typing.Union or (
                isinstance(field_type_origin, type)
                and issubclass(field_type_origin, types.UnionType)
            ):
                field_args = get_args(field.type)
                if len(field_args) == 2 and (
                    field_args[0] is type(None) and field_args[1] is not type(None)
                ):
                    return field_args[1], True
                elif len(field_args) == 2 and (
                    field_args[1] is type(None) and field_args[0] is not type(None)
                ):
                    return field_args[0], True
                else:
                    raise Exception("Not implemented - union")
            else:
                return field.type, False

        all_fields = dataclasses.fields(entity_type)

        entity_table_name = extract_entity_table_name()

        table = Table(
            entity_table_name,
            metadata,
            Column("ref_id", Integer, primary_key=True, autoincrement=True),
            Column("version", Integer, nullable=False),
            Column("archived", Boolean, nullable=False),
            Column("created_time", DateTime, nullable=False),
            Column("last_modified_time", DateTime, nullable=False),
            Column("archived_time", DateTime, nullable=True),
            keep_existing=True,
        )

        for field in all_fields:
            if field.name in (
                "ref_id",
                "version",
                "archived",
                "created_time",
                "last_modified_time",
                "archived_time",
                "events",
            ):
                continue

            field_type, field_optional = extract_field_type(field)

            if field_type == ParentLink:
                if field_optional:
                    raise Exception("Cannot have optional parent field")
                table.append_column(
                    Column(
                        field.name + "_ref_id",
                        Integer,
                        ForeignKey(
                            field.name + ".ref_id",
                        ),
                        nullable=False,
                    )
                )
            elif field_type == EntityId:
                table.append_column(
                    Column(field.name, Integer, nullable=field_optional)
                )
            elif field_type == Timestamp:
                table.append_column(
                    Column(field.name, DateTime, nullable=field_optional)
                )
            elif (
                isinstance(field_type, type)
                and get_origin(field_type) is None
                and issubclass(field_type, EntityName)
            ):
                table.append_column(
                    Column(field.name, String(100), nullable=field_optional)
                )
            elif field_type == bool:
                table.append_column(
                    Column(field.name, Boolean, nullable=field_optional)
                )
            elif field_type == int:
                table.append_column(
                    Column(field.name, Integer, nullable=field_optional)
                )
            elif field_type == float:
                table.append_column(Column(field.name, Float, nullable=field_optional))
            elif field_type == str:
                table.append_column(Column(field.name, String, nullable=field_optional))
            elif field_type == date:
                table.append_column(Column(field.name, Date, nullable=field_optional))
            elif field_type == datetime:
                table.append_column(
                    Column(field.name, DateTime, nullable=field_optional)
                )
            elif field_type == pendulum.Date:
                table.append_column(Column(field.name, Date, nullable=field_optional))
            elif field_type == pendulum.DateTime:
                table.append_column(
                    Column(field.name, DateTime, nullable=field_optional)
                )
            elif (
                isinstance(field_type, type)
                and get_origin(field_type) is None
                and issubclass(field_type, AtomicValue)
            ):
                basic_field_type = field_type.base_type_hack()
                if basic_field_type == bool:
                    table.append_column(
                        Column(field.name, Boolean, nullable=field_optional)
                    )
                elif basic_field_type == int:
                    table.append_column(
                        Column(field.name, Integer, nullable=field_optional)
                    )
                elif basic_field_type == float:
                    table.append_column(
                        Column(field.name, Float, nullable=field_optional)
                    )
                elif basic_field_type == str:
                    table.append_column(
                        Column(field.name, String, nullable=field_optional)
                    )
                elif basic_field_type == date:
                    table.append_column(
                        Column(field.name, Date, nullable=field_optional)
                    )
                elif basic_field_type == datetime:
                    table.append_column(
                        Column(field.name, DateTime, nullable=field_optional)
                    )
                elif basic_field_type == pendulum.Date:
                    table.append_column(
                        Column(field.name, Date, nullable=field_optional)
                    )
                elif basic_field_type == pendulum.DateTime:
                    table.append_column(
                        Column(field.name, DateTime, nullable=field_optional)
                    )
                else:
                    raise Exception(
                        f"Unsupported field type {field_type}+{basic_field_type} for {entity_type.__name__}:{field.name}"
                    )
            elif (
                isinstance(field_type, type)
                and get_origin(field_type) is None
                and issubclass(field_type, CompositeValue)
            ):
                table.append_column(Column(field.name, JSON, nullable=field_optional))
            elif (
                isinstance(field_type, type)
                and get_origin(field_type) is None
                and issubclass(field_type, EnumValue)
            ):
                table.append_column(Column(field.name, String, nullable=field_optional))
            elif (
                isinstance(field_type, type)
                and get_origin(field_type) is None
                and issubclass(field_type, SecretValue)
            ):
                table.append_column(Column(field.name, String, nullable=field_optional))
            elif get_origin(field_type) is not None:
                origin_field_type = get_origin(field_type)
                if origin_field_type == list:
                    table.append_column(
                        Column(field.name, JSON, nullable=field_optional)
                    )
                elif origin_field_type == set:
                    table.append_column(
                        Column(field.name, JSON, nullable=field_optional)
                    )
                elif origin_field_type == dict:
                    table.append_column(
                        Column(field.name, JSON, nullable=field_optional)
                    )
                else:
                    raise Exception(
                        f"Unsupported field type {field_type} for {entity_type.__name__}:{field.name}"
                    )
            else:
                raise Exception(
                    f"Unsupported field type {field_type} for {entity_type.__name__}:{field.name}"
                )

        return table


class _GenericAlias(Protocol):
    __origin__: type[object]


class _IndirectGenericSubclass(Protocol):
    __orig_bases__: tuple[_GenericAlias]


def _is_indirect_generic_subclass(
    obj: object,
) -> TypeGuard[_IndirectGenericSubclass]:
    if not hasattr(obj, "__orig_bases__"):
        return False
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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} and id {str(entity_id)} not found."
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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} and parent id {str(parent_ref_id)} not found."
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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} and id {str(entity_id)} not found."
            )
        return self._row_to_entity(result)


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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} and parent id {str(parent_ref_id)} not found."
            )
        return self._row_to_entity(result)


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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} identified by {ref_id} does not exist"
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
    ) -> list[_CrownEntityT]:
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
            raise self._not_found_err_cls(
                f"Entity of type {self._entity_type.__name__} identified by {ref_id} does not exist"
            )
        await self._connection.execute(
            delete(self._table).where(
                self._table.c.ref_id == ref_id.as_int(),
            ),
        )
        await remove_events(self._connection, self._event_table, ref_id)
        return self._row_to_entity(result)


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
