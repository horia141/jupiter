"""The SQLite storage engine for use cases."""
import json
import typing
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Final, Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, create_engine
from sqlalchemy.future import Engine

from jupiter.repository.sqlite.use_case.mutation_use_case_invocation_records import \
    SqliteMutationUseCaseInvocationRecordRepository
from jupiter.use_cases.infra.mutation_use_case_invocation_record_repository import \
    MutationUseCaseInvocationRecordRepository
from jupiter.use_cases.infra.storage_engine import UseCaseUnitOfWork, UseCaseStorageEngine


class SqliteUseCaseUnitOfWork(UseCaseUnitOfWork):
    """The SQLite storage unit of work."""

    _mutation_use_case_invocation_record_repository: Final[SqliteMutationUseCaseInvocationRecordRepository]

    def __init__(
            self,
            mutation_use_case_invocation_record_repository: SqliteMutationUseCaseInvocationRecordRepository) -> None:
        """Constructor."""
        self._mutation_use_case_invocation_record_repository = mutation_use_case_invocation_record_repository

    def __enter__(self) -> 'SqliteUseCaseUnitOfWork':
        """Enter the context."""
        return self

    def __exit__(
            self, _exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""

    @property
    def mutation_use_case_invocation_record_repository(self) -> MutationUseCaseInvocationRecordRepository:
        """The mutation use case invocation record repository."""
        return self._mutation_use_case_invocation_record_repository


class SqliteUseCaseStorageEngine(UseCaseStorageEngine):
    """Sqlite based Notion storage engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[Engine]
    _metadata: Final[MetaData]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_engine(config.sqlite_db_url, future=True, json_serializer=json.dumps)
        self._metadata = MetaData(bind=self._sql_engine)

    def prepare(self) -> None:
        """Prepare the environment for SQLite."""
        with self._sql_engine.begin() as connection:
            alembic_cfg = Config(str(self._config.alembic_ini_path))
            alembic_cfg.set_section_option('alembic', 'script_location', str(self._config.alembic_migrations_path))
            # pylint: disable=unsupported-assignment-operation
            alembic_cfg.attributes['connection'] = connection
            command.upgrade(alembic_cfg, 'head')

    @contextmanager
    def get_unit_of_work(self) -> typing.Iterator[UseCaseUnitOfWork]:
        """Get the unit of work."""
        with self._sql_engine.begin() as connection:
            mutation_use_case_invocation_record_repository = \
                SqliteMutationUseCaseInvocationRecordRepository(connection, self._metadata)
            yield SqliteUseCaseUnitOfWork(
                mutation_use_case_invocation_record_repository=mutation_use_case_invocation_record_repository)
