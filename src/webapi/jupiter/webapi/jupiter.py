"""The jupiter Web RPC API."""
import asyncio
import logging

import aiohttp
import jupiter.core.domain
import jupiter.core.impl.repository.sqlite.domain
import jupiter.core.use_cases
import jupiter.webapi.exceptions
from jupiter.core.domain.concept.auth.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.crm import CRM
from jupiter.core.domain.env import Env
from jupiter.core.domain.hosting import Hosting
from jupiter.core.impl.crm.noop import NoOpCRM
from jupiter.core.impl.crm.wix import WixCRM
from jupiter.core.impl.repository.sqlite.connection import SqliteConnection
from jupiter.core.impl.repository.sqlite.domain.storage_engine import (
    SqliteDomainStorageEngine,
    SqliteSearchStorageEngine,
)
from jupiter.core.impl.repository.sqlite.use_case.storage_engine import (
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
from rich.console import Console
from rich.logging import RichHandler


async def main() -> None:
    """Application main function."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RichHandler(
                console=Console(width=128),
                show_path=False,
                omit_repeated_times=False,
                rich_tracebacks=True,
                markup=True,
                enable_link_path=False,
                log_time_format="%Y-%m-%d %H:%M:%S",
            )
        ],
    )

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

    aio_session = aiohttp.ClientSession()

    global_properties = build_global_properties()

    domain_storage_engine = SqliteDomainStorageEngine.build_from_module_root(
        realm_codec_registry,
        sqlite_connection,
        jupiter.core.impl.repository.sqlite.domain,
        jupiter.core.domain,
    )
    search_storage_engine = SqliteSearchStorageEngine(
        realm_codec_registry, sqlite_connection
    )
    usecase_storage_engine = SqliteUseCaseStorageEngine(
        realm_codec_registry, sqlite_connection
    )

    crm: CRM
    if (
        global_properties.env == Env.PRODUCTION
        and global_properties.hosting == Hosting.HOSTED_GLOBAL
    ):
        crm = WixCRM(
            api_key=global_properties.wix_api_key,
            account_id=global_properties.wix_account_id,
            site_id=global_properties.wix_site_id,
            session=aio_session,
        )
    else:
        crm = NoOpCRM()

    auth_token_stamper = AuthTokenStamper(
        auth_token_secret=global_properties.auth_token_secret,
        time_provider=request_time_provider,
    )

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
        crm,
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
