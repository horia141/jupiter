"""A temporary migrator."""
import asyncio

from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.storage_engine import (
    SqliteDomainStorageEngine,
)
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.time_provider import TimeProvider


async def main() -> None:
    """Application main function."""
    # logging.basicConfig(
    #     level="info",
    #     format="%(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    #     handlers=[
    #         RichHandler(
    #             rich_tracebacks=True, markup=True, log_time_format="%Y-%m-%d %H:%M:%S"
    #         )
    #     ],
    # )
    TimeProvider()

    global_properties = build_global_properties()

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        ),
    )

    SqliteDomainStorageEngine(sqlite_connection)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
