"""A temporary migrator."""
import asyncio

import jupiter.core.domain
from jupiter.core.impl.repository.sqlite.connection import SqliteConnection
from jupiter.core.use_cases.infra.realms import ModuleExplorerRealmCodecRegistry
from jupiter.core.utils.global_properties import build_global_properties


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

    ModuleExplorerRealmCodecRegistry.build_from_module_root(jupiter.core.domain)

    global_properties = build_global_properties()

    SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        ),
    )

    # SqliteDomainStorageEngine(realm_codec_registry, sqlite_connection)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
