"""The SQLite storage engine for use cases."""
import typing
from contextlib import contextmanager
from types import TracebackType
from typing import Final, Optional

from sqlalchemy import MetaData
from sqlalchemy.future import Engine

from jupiter.repository.sqlite.connection import SqliteConnection
from jupiter.repository.sqlite.use_case.mutation_use_case_invocation_records import (
    SqliteMutationUseCaseInvocationRecordRepository,
)
from jupiter.use_cases.infra.mutation_use_case_invocation_record_repository import (
    MutationUseCaseInvocationRecordRepository,
)
from jupiter.use_cases.infra.storage_engine import (
    UseCaseUnitOfWork,
    UseCaseStorageEngine,
)


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
        _exc_type: Optional[typing.Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context."""

    @property
    def mutation_use_case_invocation_record_repository(
        self,
    ) -> MutationUseCaseInvocationRecordRepository:
        """The mutation use case invocation record repository."""
        return self._mutation_use_case_invocation_record_repository


class SqliteUseCaseStorageEngine(UseCaseStorageEngine):
    """Sqlite based Notion storage engine."""

    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, connection: SqliteConnection) -> None:
        """Constructor."""
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[UseCaseUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            mutation_use_case_invocation_record_repository = (
                SqliteMutationUseCaseInvocationRecordRepository(
                    connection, self._metadata
                )
            )
            yield SqliteUseCaseUnitOfWork(
                mutation_use_case_invocation_record_repository=mutation_use_case_invocation_record_repository
            )
