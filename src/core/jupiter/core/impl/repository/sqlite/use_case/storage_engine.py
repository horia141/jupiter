"""The SQLite storage engine for use cases."""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Final

from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.impl.repository.sqlite.connection import SqliteConnection
from jupiter.core.impl.repository.sqlite.use_case.mutation_use_case_invocation_records import (
    SqliteMutationUseCaseInvocationRecordRepository,
)
from jupiter.core.use_cases.infra.mutation_use_case_invocation_record_repository import (
    MutationUseCaseInvocationRecordRepository,
)
from jupiter.core.use_cases.infra.storage_engine import (
    UseCaseStorageEngine,
    UseCaseUnitOfWork,
)
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine


class SqliteUseCaseUnitOfWork(UseCaseUnitOfWork):
    """The SQLite storage unit of work."""

    _mutation_use_case_invocation_record_repository: Final[
        SqliteMutationUseCaseInvocationRecordRepository
    ]

    def __init__(
        self,
        mutation_use_case_invocation_record_repository: SqliteMutationUseCaseInvocationRecordRepository,
    ) -> None:
        """Constructor."""
        self._mutation_use_case_invocation_record_repository = (
            mutation_use_case_invocation_record_repository
        )

    def __enter__(self) -> "SqliteUseCaseUnitOfWork":
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
    def mutation_use_case_invocation_record_repository(
        self,
    ) -> MutationUseCaseInvocationRecordRepository:
        """The mutation use case invocation record repository."""
        return self._mutation_use_case_invocation_record_repository


class SqliteUseCaseStorageEngine(UseCaseStorageEngine):
    """Sqlite based use case storage engine."""

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
    async def get_unit_of_work(self) -> AsyncIterator[UseCaseUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            mutation_use_case_invocation_record_repository = (
                SqliteMutationUseCaseInvocationRecordRepository(
                    self._realm_codec_registry,
                    connection,
                    self._metadata,
                )
            )
            yield SqliteUseCaseUnitOfWork(
                mutation_use_case_invocation_record_repository=mutation_use_case_invocation_record_repository,
            )
