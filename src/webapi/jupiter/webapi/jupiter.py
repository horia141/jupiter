"""The Jupiter Web RPC API."""
import asyncio

import aiohttp
import jupiter.core.domain
import jupiter.core.repository.sqlite.domain
import jupiter.core.use_cases
import jupiter.webapi.exceptions
from jupiter.core.domain.auth.auth_token_stamper import AuthTokenStamper
from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.storage_engine import (
    SqliteDomainStorageEngine,
    SqliteSearchStorageEngine,
)
from jupiter.core.repository.sqlite.use_case.storage_engine import (
    SqliteUseCaseStorageEngine,
)
from jupiter.core.use_cases.infra.persistent_mutation_use_case_recoder import (
    PersistentMutationUseCaseInvocationRecorder,
)
from jupiter.core.use_cases.infra.realms import ModuleExplorerRealmCodecRegistry
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.webapi.app import WebServiceApp
from jupiter.webapi.time_provider import CronRunTimeProvider, PerRequestTimeProvider
from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory


async def main() -> None:
    """Application main function."""
    request_time_provider = PerRequestTimeProvider()
    cron_run_time_provider = CronRunTimeProvider()

    no_timezone_global_properties = build_global_properties()

    realm_codec_registry = ModuleExplorerRealmCodecRegistry.build_from_module_root(
        jupiter.core.domain, jupiter.core.use_cases
    )

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            no_timezone_global_properties.sqlite_db_url,
            no_timezone_global_properties.alembic_ini_path,
            no_timezone_global_properties.alembic_migrations_path,
        ),
    )

    global_properties = build_global_properties()

    domain_storage_engine = SqliteDomainStorageEngine.build_from_module_root(
        realm_codec_registry,
        sqlite_connection,
        jupiter.core.repository.sqlite.domain,
        jupiter.core.domain,
    )
    search_storage_engine = SqliteSearchStorageEngine(
        realm_codec_registry, sqlite_connection
    )
    usecase_storage_engine = SqliteUseCaseStorageEngine(
        realm_codec_registry, sqlite_connection
    )

    auth_token_stamper = AuthTokenStamper(
        auth_token_secret=global_properties.auth_token_secret,
        time_provider=request_time_provider,
    )

    aio_session = aiohttp.ClientSession()

    progress_reporter_factory = WebsocketProgressReporterFactory()

    invocation_recorder = PersistentMutationUseCaseInvocationRecorder(
        storage_engine=usecase_storage_engine,
    )

    web_app = WebServiceApp.build_from_module_root(
        global_properties,
        request_time_provider,
        cron_run_time_provider,
        invocation_recorder,
        progress_reporter_factory,
        realm_codec_registry,
        auth_token_stamper,
        domain_storage_engine,
        search_storage_engine,
        usecase_storage_engine,
        jupiter.core.use_cases,
        jupiter.webapi.exceptions,
    )

    await sqlite_connection.prepare()

    try:
        await web_app.run()
    finally:
        try:
            await sqlite_connection.dispose()
        finally:
            pass
        try:
            await aio_session.close()
        finally:
            pass
        try:
            await progress_reporter_factory.unregister_all_websockets()
        finally:
            pass


def sync_main() -> None:
    """Run the main function synchronously."""
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
