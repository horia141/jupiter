"""The SQLite connection."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.future import Engine

from jupiter.framework.storage import Connection


class SqliteConnection(Connection):
    """A connection to the file backed Sqlite storage engine."""

    @dataclass(frozen=True)
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[Engine]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_engine(
            config.sqlite_db_url, future=True, json_serializer=json.dumps
        )

    def prepare(self) -> None:
        """Prepare the Sqlite storage."""
        with self._sql_engine.begin() as connection:
            alembic_cfg = Config(str(self._config.alembic_ini_path))
            alembic_cfg.set_section_option(
                "alembic", "script_location", str(self._config.alembic_migrations_path)
            )
            # pylint: disable=unsupported-assignment-operation
            alembic_cfg.attributes["connection"] = connection
            command.upgrade(alembic_cfg, "head")

    def nuke(self) -> None:
        """Completely destroy the Sqlite storage."""
        real_path = self._config.sqlite_db_url.replace("sqlite+pysqlite:///", "")
        os.remove(real_path)

    @property
    def sql_engine(self) -> Engine:
        """The raw SQLite engine object."""
        return self._sql_engine
