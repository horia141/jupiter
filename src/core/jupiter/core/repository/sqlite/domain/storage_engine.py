"""The real implementation of an engine."""
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from types import GenericAlias, ModuleType, TracebackType
from typing import (
    Final,
    Generic,
    TypeVar,
    cast,
    get_args,
    get_origin,
    overload,
)

from jupiter.core.domain.application.search.infra.search_repository import (
    SearchRepository,
)
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
    SearchUnitOfWork,
)
from jupiter.core.framework.entity import (
    CrownEntity,
    Entity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.record import Record
from jupiter.core.framework.repository import (
    CrownEntityRepository,
    EntityRepository,
    RecordRepository,
    Repository,
    RootEntityRepository,
    StubEntityRepository,
    TrunkEntityRepository,
)
from jupiter.core.framework.utils import find_all_modules
from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.application.search import (
    SqliteSearchRepository,
)
from jupiter.core.repository.sqlite.infra.repository import (
    SqliteCrownEntityRepository,
    SqliteEntityRepository,
    SqliteRecordRepository,
    SqliteRepository,
    SqliteRootEntityRepository,
    SqliteStubEntityRepository,
    SqliteTrunkEntityRepository,
)
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

_RepositoryT = TypeVar("_RepositoryT", bound=Repository)
_RootEntityT = TypeVar("_RootEntityT", bound=RootEntity)
_StubEntityT = TypeVar("_StubEntityT", bound=StubEntity)
_TrunkEntityT = TypeVar("_TrunkEntityT", bound=TrunkEntity)
_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)
_RecordT = TypeVar("_RecordT", bound=Record)


class SqliteDomainUnitOfWork(DomainUnitOfWork):
    """A Sqlite specific unit of work."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _connection: Final[AsyncConnection]
    _metadata: Final[MetaData]
    _entity_repository_factories: Final[
        dict[type[Entity], type[SqliteEntityRepository[Entity]]]
    ]
    _record_repository_factories: Final[
        dict[type[Record], type[SqliteRecordRepository[Record, object]]]
    ]
    _repository_factories: Final[dict[type[Repository], type[SqliteRepository]]]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        entity_repository_factories: dict[
            type[Entity], type[SqliteEntityRepository[Entity]]
        ],
        record_repository_factories: dict[
            type[Record], type[SqliteRecordRepository[Record, object]]
        ],
        repository_factories: dict[type[Repository], type[SqliteRepository]],
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._connection = connection
        self._metadata = metadata
        self._entity_repository_factories = entity_repository_factories
        self._record_repository_factories = record_repository_factories
        self._repository_factories = repository_factories

    def __enter__(self) -> "SqliteDomainUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Exit context."""

    def get(self, repository_type: type[_RepositoryT]) -> _RepositoryT:
        """Retrieve a repository."""
        if repository_type not in self._repository_factories:
            raise ValueError(f"No repository for type: {repository_type}")

        factory = self._repository_factories[repository_type]

        repository = factory(
            self._realm_codec_registry, self._connection, self._metadata
        )

        return cast(_RepositoryT, repository)

    @overload
    def get_for(
        self, entity_type: type[_RootEntityT]
    ) -> RootEntityRepository[_RootEntityT]:
        ...

    @overload
    def get_for(
        self, entity_type: type[_StubEntityT]
    ) -> StubEntityRepository[_StubEntityT]:
        ...

    @overload
    def get_for(
        self, entity_type: type[_TrunkEntityT]
    ) -> TrunkEntityRepository[_TrunkEntityT]:
        ...

    @overload
    def get_for(
        self, entity_type: type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        ...

    def get_for(
        self,
        entity_type: type[_RootEntityT]
        | type[_StubEntityT]
        | type[_TrunkEntityT]
        | type[_CrownEntityT],
    ) -> RootEntityRepository[_RootEntityT] | StubEntityRepository[
        _StubEntityT
    ] | TrunkEntityRepository[_TrunkEntityT] | CrownEntityRepository[_CrownEntityT]:
        """Return a repository for a particular entity."""
        if entity_type not in self._entity_repository_factories:
            raise ValueError(f"No repository for entity type: {entity_type}")
        factory = self._entity_repository_factories[entity_type]

        repository = factory(
            self._realm_codec_registry, self._connection, self._metadata
        )

        if issubclass(entity_type, RootEntity):
            return cast(
                RootEntityRepository[_RootEntityT],
                repository,
            )
        if issubclass(entity_type, StubEntity):
            return cast(
                StubEntityRepository[_StubEntityT],
                repository,
            )
        if issubclass(entity_type, TrunkEntity):
            return cast(
                TrunkEntityRepository[_TrunkEntityT],
                repository,
            )
        if issubclass(entity_type, CrownEntity):
            return cast(
                CrownEntityRepository[_CrownEntityT],
                repository,
            )

    def get_for_record(
        self, record_type: type[_RecordT]
    ) -> RecordRepository[_RecordT, object]:
        """Return a repository for a particular record."""
        if record_type not in self._record_repository_factories:
            raise ValueError(f"No repository for record type: {record_type}")
        factory = self._record_repository_factories[record_type]

        repository = factory(
            self._realm_codec_registry, self._connection, self._metadata
        )

        return cast(RecordRepository[_RecordT, object], repository)


class _StandardSqliteRootEntityRepository(
    Generic[_RootEntityT],
    SqliteRootEntityRepository[_RootEntityT],
    RootEntityRepository[_RootEntityT],
):
    """A standard repository for root entities."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        the_type: type[_RootEntityT],
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry, connection, metadata, entity_type=the_type
        )


class _StandardSqliteStubEntityRepository(
    Generic[_StubEntityT],
    SqliteStubEntityRepository[_StubEntityT],
    StubEntityRepository[_StubEntityT],
):
    """A standard repository for stub entities."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        the_type: type[_StubEntityT],
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry, connection, metadata, entity_type=the_type
        )


class _StandardSqliteTrunkEntityRepository(
    Generic[_TrunkEntityT],
    SqliteTrunkEntityRepository[_TrunkEntityT],
    TrunkEntityRepository[_TrunkEntityT],
):
    """A standard repository for trunk entities."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        the_type: type[_TrunkEntityT],
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry, connection, metadata, entity_type=the_type
        )


class _StandardSqliteCrownEntityRepository(
    Generic[_CrownEntityT],
    SqliteCrownEntityRepository[_CrownEntityT],
    CrownEntityRepository[_CrownEntityT],
):
    """A standard repository for crown entities."""

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: AsyncConnection,
        metadata: MetaData,
        the_type: type[_CrownEntityT],
    ) -> None:
        """Constructor."""
        super().__init__(
            realm_codec_registry, connection, metadata, entity_type=the_type
        )


class SqliteDomainStorageEngine(DomainStorageEngine):
    """An Sqlite specific engine."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]
    _entity_repository_factories: Final[
        dict[type[Entity], type[SqliteEntityRepository[Entity]]]
    ]
    _record_repository_factories: Final[
        dict[type[Record], type[SqliteRecordRepository[Record, object]]]
    ]
    _repository_factories: Final[dict[type[Repository], type[SqliteRepository]]]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        connection: SqliteConnection,
        entity_repository_factories: dict[
            type[Entity], type[SqliteEntityRepository[Entity]]
        ],
        record_repository_factories: dict[
            type[Record], type[SqliteRecordRepository[Record, object]]
        ],
        repository_factories: dict[type[Repository], type[SqliteRepository]],
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)
        self._entity_repository_factories = entity_repository_factories
        self._record_repository_factories = record_repository_factories
        self._repository_factories = repository_factories

    @staticmethod
    def build_from_module_root(
        realm_codec_registry: RealmCodecRegistry,
        connection: SqliteConnection,
        *module_roots: ModuleType,
    ) -> "SqliteDomainStorageEngine":
        """Build a unit of work from module roots."""

        def figure_out_entity(the_type: type[Repository]) -> type[Entity] | None:
            """Figure out the entity type from the repository type."""
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Entity):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_entity(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def figure_out_record(the_type: type[Repository]) -> type[Record] | None:
            """Figure out the entity type from the repository type."""
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                base_args = get_args(base)
                if len(base_args) == 0:
                    continue
                for base_arg in base_args:
                    if isinstance(base_arg, type) and issubclass(base_arg, Record):
                        return base_arg

                origin_base = cast(type | GenericAlias, get_origin(base))
                if origin_base != base:
                    possible_concept_type = figure_out_record(
                        cast(type, origin_base)
                    )  # We know better!
                    if possible_concept_type is not None:
                        return possible_concept_type

            return None

        def figure_out_abstract_entity_repository(
            the_type: type[Repository],
        ) -> type[EntityRepository[Entity]] | None:
            """Figure out the abstract repository type from the repository type."""
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                if not isinstance(base, type):
                    continue
                if not issubclass(base, Repository):
                    continue
                if not issubclass(base, EntityRepository):
                    continue
                return base  # A hack, we might be finding it too fast!

            return None

        def figure_out_abstract_record_repository(
            the_type: type[Repository],
        ) -> type[RecordRepository[Record, object]] | None:
            """Figure out the abstract repository type from the repository type."""
            if not hasattr(the_type, "__orig_bases__"):
                return None

            for base in the_type.__orig_bases__:
                if not isinstance(base, type):
                    continue
                if not issubclass(base, Repository):
                    continue
                if not issubclass(base, RecordRepository):
                    continue
                return base  # A hack, we might be finding it too fast!

            return None

        def figure_out_abstract_repository(
            the_type: type[Repository],
        ) -> type[Repository] | None:
            """Figure out the abstract repository type from the repository type."""
            for base in the_type.mro()[1:]:
                if not issubclass(base, Repository):
                    continue
                return base  # A hack, we might be finding it too fast!

            return None

        def extract_entity_repositories(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[
                type[Entity],
                type[EntityRepository[Entity]],
                type[SqliteEntityRepository[Entity]],
            ]
        ]:
            """Extract all entity repositories from a module."""
            for _name, obj in the_module.__dict__.items():
                if not isinstance(obj, type):
                    continue
                if not issubclass(obj, Repository):
                    continue
                if not issubclass(obj, EntityRepository):
                    continue
                if not issubclass(obj, SqliteEntityRepository):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:  # type: ignore
                    # This is not a concret type and we can move on
                    continue

                entity_type = figure_out_entity(cast(type, obj))
                if entity_type is None:
                    raise Exception(
                        f"Could not figure out entity type for repository: {obj}"
                    )

                abstract_repository_type = figure_out_abstract_entity_repository(
                    cast(type, obj)
                )
                if abstract_repository_type is None:
                    raise Exception(
                        f"Could not figure out abstract repository type for repository: {obj}"
                    )

                yield entity_type, abstract_repository_type, obj

        def extract_record_repositories(
            the_module: ModuleType,
        ) -> Iterator[
            tuple[
                type[Record],
                type[RecordRepository[Record, object]],
                type[SqliteRecordRepository[Record, object]],
            ]
        ]:
            """Extract all record repositories from a module."""
            for _name, obj in the_module.__dict__.items():
                if not isinstance(obj, type):
                    continue
                if not issubclass(obj, Repository):
                    continue
                if not issubclass(obj, RecordRepository):
                    continue
                if not issubclass(obj, SqliteRecordRepository):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:  # type: ignore
                    # This is not a concret type and we can move on
                    continue

                record_type = figure_out_record(cast(type, obj))
                if record_type is None:
                    raise Exception(
                        f"Could not figure out record type for repository: {obj}"
                    )

                abstract_repository_type = figure_out_abstract_record_repository(
                    cast(type, obj)
                )

                if abstract_repository_type is None:
                    raise Exception(
                        f"Could not figure out abstract repository type for repository: {obj}"
                    )

                yield record_type, abstract_repository_type, obj

        def extract_repositories(
            the_module: ModuleType,
        ) -> Iterator[tuple[type[Repository], type[SqliteRepository]]]:
            """Extract all repositories from a module."""
            for _name, obj in the_module.__dict__.items():
                if not isinstance(obj, type):
                    continue
                if not issubclass(obj, Repository):
                    continue
                if not issubclass(obj, SqliteRepository):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                abstract_repository_type = figure_out_abstract_repository(
                    cast(type, obj)
                )
                if abstract_repository_type is None:
                    raise Exception(
                        f"Could not figure out abstract repository type for repository: {obj}"
                    )
                yield abstract_repository_type, obj

        def extract_entities(
            the_module: ModuleType,
        ) -> Iterator[type[Entity]]:
            for _name, obj in the_module.__dict__.items():
                if not (isinstance(obj, type) and issubclass(obj, Entity)):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                yield obj

        entity_repository_factories = {}
        record_repository_factories = {}
        repository_factories: dict[type[Repository], type[SqliteRepository]] = {}

        for m in find_all_modules(*module_roots):
            # extract all entity repositories
            for (
                entity_type,
                abstract_entity_repository_type,
                concrete_entity_repository_type,
            ) in extract_entity_repositories(m):
                if entity_type in entity_repository_factories:
                    raise Exception(
                        f"Entity type {entity_type} already has a repository"
                    )
                entity_repository_factories[
                    entity_type
                ] = concrete_entity_repository_type
                if abstract_entity_repository_type in repository_factories:
                    raise Exception(
                        f"Abstract repository type {abstract_entity_repository_type} already has a repository"
                    )
                repository_factories[
                    abstract_entity_repository_type
                ] = concrete_entity_repository_type

            # extract all record repositories
            for (
                record_type,
                abstract_record_repository_type,
                concrete_record_repository_type,
            ) in extract_record_repositories(m):
                if record_type in record_repository_factories:
                    raise Exception(
                        f"Record type {record_type} already has a repository"
                    )
                record_repository_factories[
                    record_type
                ] = concrete_record_repository_type
                if abstract_record_repository_type in repository_factories:
                    raise Exception(
                        f"Abstract repository type {abstract_record_repository_type} already has a repository"
                    )
                repository_factories[
                    abstract_record_repository_type
                ] = concrete_record_repository_type

            # extract all random repositories
            for (
                abstract_repository_type,
                concrete_repository_type,
            ) in extract_repositories(m):
                if abstract_repository_type in repository_factories:
                    continue
                repository_factories[
                    abstract_repository_type
                ] = concrete_repository_type

            # look at all entities and build repositories for them
            for entity_type in extract_entities(m):
                if entity_type in entity_repository_factories:
                    continue
                if issubclass(entity_type, RootEntity):
                    entity_repository_factories[entity_type] = type(
                        f"_StandardSqliteRootEntityRepository_{entity_type.__name__}",
                        (_StandardSqliteRootEntityRepository,),
                        {"__init__": _generic_root_init(entity_type)},
                    )
                elif issubclass(entity_type, StubEntity):
                    entity_repository_factories[entity_type] = type(
                        f"_StandardSqliteStubEntityRepository_{entity_type.__name__}",
                        (_StandardSqliteStubEntityRepository,),
                        {"__init__": _generic_stub_init(entity_type)},
                    )
                elif issubclass(entity_type, TrunkEntity):
                    entity_repository_factories[entity_type] = type(
                        f"_StandardSqliteTrunkEntityRepository_{entity_type.__name__}",
                        (_StandardSqliteTrunkEntityRepository,),
                        {"__init__": _generic_trunk_init(entity_type)},
                    )
                elif issubclass(entity_type, CrownEntity):
                    entity_repository_factories[entity_type] = type(
                        f"_StandardSqliteCrownEntityRepository_{entity_type.__name__}",
                        (_StandardSqliteCrownEntityRepository,),
                        {"__init__": _generic_crown_init(entity_type)},
                    )
                else:
                    raise Exception(f"Unknown entity type: {entity_type}")

        return SqliteDomainStorageEngine(
            realm_codec_registry,
            connection,
            entity_repository_factories,
            record_repository_factories,
            repository_factories,
        )

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[DomainUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            yield SqliteDomainUnitOfWork(
                realm_codec_registry=self._realm_codec_registry,
                connection=connection,
                metadata=self._metadata,
                entity_repository_factories=self._entity_repository_factories,
                record_repository_factories=self._record_repository_factories,
                repository_factories=self._repository_factories,
            )


def _generic_root_init(
    entity_type: type[_RootEntityT],
) -> Callable[
    [
        _StandardSqliteRootEntityRepository[_RootEntityT],
        RealmCodecRegistry,
        AsyncConnection,
        MetaData,
    ],
    None,
]:
    """Generic constructor for root entities."""
    return lambda self, realm_codec_registry, connection, metadata: super(
        _StandardSqliteRootEntityRepository, self
    ).__init__(realm_codec_registry, connection, metadata, entity_type=entity_type)


def _generic_stub_init(
    entity_type: type[_StubEntityT],
) -> Callable[
    [
        _StandardSqliteStubEntityRepository[_StubEntityT],
        RealmCodecRegistry,
        AsyncConnection,
        MetaData,
    ],
    None,
]:
    """Generic constructor for stub entities."""
    return lambda self, realm_codec_registry, connection, metadata: super(
        _StandardSqliteStubEntityRepository, self
    ).__init__(realm_codec_registry, connection, metadata, entity_type=entity_type)


def _generic_trunk_init(
    entity_type: type[_TrunkEntityT],
) -> Callable[
    [
        _StandardSqliteTrunkEntityRepository[_TrunkEntityT],
        RealmCodecRegistry,
        AsyncConnection,
        MetaData,
    ],
    None,
]:
    """Generic constructor for trunk entities."""
    return lambda self, realm_codec_registry, connection, metadata: super(
        _StandardSqliteTrunkEntityRepository, self
    ).__init__(realm_codec_registry, connection, metadata, entity_type=entity_type)


def _generic_crown_init(
    entity_type: type[_CrownEntityT],
) -> Callable[
    [
        _StandardSqliteCrownEntityRepository[_CrownEntityT],
        RealmCodecRegistry,
        AsyncConnection,
        MetaData,
    ],
    None,
]:
    """Generic constructor for crown entities."""
    return lambda self, realm_codec_registry, connection, metadata: super(
        _StandardSqliteCrownEntityRepository, self
    ).__init__(realm_codec_registry, connection, metadata, entity_type=entity_type)


class SqliteSearchUnitOfWork(SearchUnitOfWork):
    """A Sqlite specific search unit of work."""

    _search_repository: Final[SqliteSearchRepository]

    def __init__(self, search_repository: SqliteSearchRepository) -> None:
        """Constructor."""
        self._search_repository = search_repository

    def __enter__(self) -> "SqliteSearchUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        """Exit context."""

    @property
    def search_repository(self) -> SearchRepository:
        """The search repository."""
        return self._search_repository


class SqliteSearchStorageEngine(SearchStorageEngine):
    """An Sqlite specific engine."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, connection: SqliteConnection
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[SearchUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            search_repository = SqliteSearchRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            yield SqliteSearchUnitOfWork(search_repository=search_repository)
