"""The SQLite connection."""
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Final

import sqlalchemy.exc
from alembic import command
from alembic.config import Config
from jupiter.core.framework.storage import Connection, ConnectionPrepareError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from pydantic.json import pydantic_encoder


class SqliteConnection(Connection):
    """A connection to the file backed Sqlite storage engine."""

    @dataclass
    class Config:
        """Config for a Sqlite metric engine."""

        sqlite_db_url: str
        alembic_ini_path: Path
        alembic_migrations_path: Path

    _config: Final[Config]
    _sql_engine: Final[AsyncEngine]

    def __init__(self, config: Config) -> None:
        """Constructor."""
        self._config = config
        self._sql_engine = create_async_engine(
            config.sqlite_db_url,
            future=True,
            json_serializer=lambda *a, **kw: json.dumps(
                *a, **kw, default=pydantic_encoder
            ),
        )

    async def prepare(self) -> None:
        """Prepare the Sqlite storage."""
        try:
            async with self._sql_engine.begin() as connection:
                alembic_cfg = Config(str(self._config.alembic_ini_path))
                alembic_cfg.set_section_option(
                    "alembic",
                    "script_location",
                    str(self._config.alembic_migrations_path),
                )
                alembic_cfg.attributes["connection"] = connection
                command.upgrade(alembic_cfg, "head")
        except sqlalchemy.exc.OperationalError as exc:
            raise ConnectionPrepareError("Failed to prepare Sqlite connection") from exc

    async def dispose(self) -> None:
        """Close the Sqlite storage."""
        await self._sql_engine.dispose()

    def nuke(self) -> None:
        """Completely destroy the Sqlite storage."""
        real_path = self._config.sqlite_db_url.replace("sqlite+pysqlite:///", "")
        Path(real_path).unlink()

    @property
    def sql_engine(self) -> AsyncEngine:
        """The raw SQLite engine object."""
        return self._sql_engine
