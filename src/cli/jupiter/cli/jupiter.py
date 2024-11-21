"""The CLI entry-point for jupiter."""
import asyncio
import logging
import sys

import jupiter.cli.command
import jupiter.core.domain
import jupiter.core.repository.sqlite.domain
import jupiter.core.use_cases
from jupiter.cli.command.command import CliApp
from jupiter.cli.command.rendering import RichConsoleProgressReporterFactory
from jupiter.cli.session_storage import SessionStorage
from jupiter.cli.top_level_context import TopLevelContext
from jupiter.core.domain.concept.auth.auth_token_stamper import AuthTokenStamper
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
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from jupiter.core.use_cases.load_top_level_info import (
    LoadTopLevelInfoArgs,
    LoadTopLevelInfoUseCase,
)
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console

# import coverage


async def main() -> None:
    """Application main function."""
    logging.disable()

    time_provider = TimeProvider()

    global_properties = build_global_properties()

    realm_codec_registry = ModuleExplorerRealmCodecRegistry.build_from_module_root(
        jupiter.core.domain, jupiter.core.use_cases
    )

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        ),
    )

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

    session_storage = SessionStorage(
        global_properties.session_info_path, realm_codec_registry
    )

    auth_token_stamper = AuthTokenStamper(
        auth_token_secret=global_properties.auth_token_secret,
        time_provider=time_provider,
    )

    invocation_recorder = PersistentMutationUseCaseInvocationRecorder(
        usecase_storage_engine,
    )

    console = Console()

    progress_reporter_factory = RichConsoleProgressReporterFactory(console)

    load_top_level_info_use_case = LoadTopLevelInfoUseCase(
        global_properties=global_properties,
        time_provider=time_provider,
        realm_codec_registry=realm_codec_registry,
        auth_token_stamper=auth_token_stamper,
        domain_storage_engine=domain_storage_engine,
        search_storage_engine=search_storage_engine,
    )

    await sqlite_connection.prepare()

    session_info = session_storage.load_optional()
    guest_session = AppGuestUseCaseSession(
        session_info.auth_token_ext if session_info else None
    )
    _, top_level_info = await load_top_level_info_use_case.execute(
        guest_session, LoadTopLevelInfoArgs()
    )

    top_level_context = TopLevelContext(
        default_workspace_name=top_level_info.deafult_workspace_name,
        default_first_project_name=top_level_info.default_root_project_name,
        user=top_level_info.user,
        workspace=top_level_info.workspace,
    )

    cli_app = CliApp.build_from_module_root(
        global_properties,
        top_level_context,
        console,
        time_provider,
        invocation_recorder,
        progress_reporter_factory,
        realm_codec_registry,
        session_storage,
        auth_token_stamper,
        domain_storage_engine,
        search_storage_engine,
        usecase_storage_engine,
        jupiter.core.use_cases,
        jupiter.cli.command,
    )

    try:
        await cli_app.run(sys.argv)
    finally:
        await sqlite_connection.dispose()


# coverage.process_startup()  # type: ignore

if __name__ == "__main__":
    asyncio.run(main())
