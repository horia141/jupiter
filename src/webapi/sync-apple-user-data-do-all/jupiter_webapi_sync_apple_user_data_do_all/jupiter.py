"""The Sync Apple user data WebAPI cron."""

import asyncio
import sys

import jupiter.core
from jupiter.core.apps.crm.crm import CRM, CrmDeploymentContext
from jupiter.core.apps.crm.impl.noop import NoOpCRM
from jupiter.core.apps.crm.impl.postgres.indexing_storage_engine import (
    PostgresCRMIndexingStorageEngine,
)
from jupiter.core.apps.crm.impl.sqlite.indexing_storage_engine import (
    SqliteCRMIndexingStorageEngine,
)
from jupiter.core.apps.crm.impl.wix import WixCRM
from jupiter.core.apps.crm.indexing_storage_engine import CRMIndexingStorageEngine
from jupiter.core.auth.sub.apple.oauth_client import AppleOauthClient
from jupiter.core.auth.sub.apple.use_case.sync_apple_user_data_do_all import (
    SyncAppleUserDataDoAllUseCase,
)
from jupiter.core.auth.sub.email_verification.impl.noop import NoOpEmailSender
from jupiter.core.backend_blend import (
    JupiterCrmBackend,
    JupiterTelemetry,
    JupiterWebApiSearchBackend,
    JupiterWebApiStorageEngine,
)
from jupiter.core.common.search.impl.algolia.storage_engine import (
    AlgoliaSearchStorageEngine,
    AlgoliaSearchStorageEngineConfig,
)
from jupiter.core.common.search.impl.postgres.indexing_storage_engine import (
    PostgresSearchIndexingStorageEngine,
)
from jupiter.core.common.search.impl.postgres.storage_engine import (
    PostgresSearchStorageEngine,
)
from jupiter.core.common.search.impl.sqlite.indexing_storage_engine import (
    SqliteSearchIndexingStorageEngine,
)
from jupiter.core.common.search.impl.sqlite.storage_engine import (
    SqliteSearchStorageEngine,
)
from jupiter.core.common.search.indexing_storage_engine import (
    SearchIndexingStorageEngine,
)
from jupiter.core.common.search.storage_engine import SearchStorageEngine
from jupiter.core.common.sub.locations.resolver.impl.noop import NoOpLocationResolver
from jupiter.core.config import JupiterPorts, build_global_properties
from jupiter.framework.concepts.standard import ModuleExplorerConceptRegistry
from jupiter.framework.mutation_inovcation.recorders.impl.postgres import (
    PostgresMutationInvocationStorageEngine,
)
from jupiter.framework.mutation_inovcation.recorders.impl.sqlite import (
    SqliteMutationInvocationStorageEngine,
)
from jupiter.framework.mutation_inovcation.recorders.persistent import (
    MutationInvocationStorageEngine,
    PersistentMutationInvocationRecorder,
)
from jupiter.framework.realm.standard import ModuleExplorerRealmCodecRegistry
from jupiter.framework.storage.postgres.connection import PostgresConnection
from jupiter.framework.storage.postgres.storage_engine import (
    PostgresDomainStorageEngine,
)
from jupiter.framework.storage.repository import DomainStorageEngine
from jupiter.framework.storage.sqlite.connection import SqliteConnection
from jupiter.framework.storage.sqlite.storage_engine import (
    SqliteDomainStorageEngine,
)
from jupiter.framework.telemetry.local.local import LocalTelemetry
from jupiter.framework.telemetry.sentry.sentry import SentryTelemetry
from jupiter.framework.telemetry.telemetry import Telemetry
from jupiter.framework.time_provider import CronRunTimeProvider
from rich import print as rich_print

import jupiter_webapi_sync_apple_user_data_do_all.config
import jupiter_webapi_sync_apple_user_data_do_all.exceptions
from jupiter_webapi_sync_apple_user_data_do_all.config import (
    JupiterExceptionHandler,
    JupiterWebApiCronForm,
    build_web_api_properties,
)


async def main() -> None:
    """Application main function."""
    global_properties = build_global_properties()
    service_properties = build_web_api_properties()

    realm_codec_registry = ModuleExplorerRealmCodecRegistry.build_from_module_root(
        jupiter.core
    )
    concept_registry = ModuleExplorerConceptRegistry.build_from_module_root(
        jupiter.core
    )
    cron_run_time_provider = CronRunTimeProvider()

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            service_properties.sqlite_db_url,
            service_properties.alembic_ini_path,
            service_properties.alembic_migrations_path,
        ),
    )

    postgres_connection = PostgresConnection(
        PostgresConnection.Config(
            service_properties.postgres_db_url,
            service_properties.alembic_ini_path,
            service_properties.alembic_migrations_path,
        ),
    )

    telemetry: Telemetry
    if service_properties.telemetry == JupiterTelemetry.SENTRY:
        telemetry = SentryTelemetry(service_properties.sentry_dsn)
    else:
        telemetry = LocalTelemetry()

    telemetry.prepare()

    mutation_invocation_storage_engine: MutationInvocationStorageEngine
    if service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
        mutation_invocation_storage_engine = SqliteMutationInvocationStorageEngine(
            realm_codec_registry, sqlite_connection
        )
    else:
        mutation_invocation_storage_engine = PostgresMutationInvocationStorageEngine(
            realm_codec_registry, postgres_connection
        )

    invocation_recorder = PersistentMutationInvocationRecorder(
        storage_engine=mutation_invocation_storage_engine,
    )

    domain_storage_engine: DomainStorageEngine
    if service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
        domain_storage_engine = SqliteDomainStorageEngine.build_from_module_root(
            realm_codec_registry, sqlite_connection, jupiter.core
        )
    else:
        domain_storage_engine = PostgresDomainStorageEngine.build_from_module_root(
            realm_codec_registry, postgres_connection, jupiter.core
        )

    search_storage_engine: SearchStorageEngine
    if service_properties.search_backend == JupiterWebApiSearchBackend.ALGOLIA:
        search_storage_engine = AlgoliaSearchStorageEngine(
            realm_codec_registry,
            AlgoliaSearchStorageEngineConfig(
                app_id=service_properties.algolia_app_id,
                write_api_key=service_properties.algolia_write_api_key,
                universe=global_properties.universe,
                env=global_properties.env,
                instance=global_properties.instance,
            ),
        )
    elif service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
        search_storage_engine = SqliteSearchStorageEngine(
            realm_codec_registry, sqlite_connection
        )
    else:
        search_storage_engine = PostgresSearchStorageEngine(
            realm_codec_registry, postgres_connection
        )

    search_indexing_storage_engine: SearchIndexingStorageEngine
    if service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
        search_indexing_storage_engine = SqliteSearchIndexingStorageEngine(
            realm_codec_registry, sqlite_connection
        )
    else:
        search_indexing_storage_engine = PostgresSearchIndexingStorageEngine(
            realm_codec_registry, postgres_connection
        )

    crm_indexing_storage_engine: CRMIndexingStorageEngine
    if service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
        crm_indexing_storage_engine = SqliteCRMIndexingStorageEngine(
            realm_codec_registry, sqlite_connection
        )
    else:
        crm_indexing_storage_engine = PostgresCRMIndexingStorageEngine(
            realm_codec_registry, postgres_connection
        )

    deployment = CrmDeploymentContext(
        universe=global_properties.universe,
        env=global_properties.env,
        instance=global_properties.instance,
    )
    crm: CRM
    if global_properties.crm_backend == JupiterCrmBackend.WIX:
        crm = WixCRM(
            api_key=service_properties.wix_api_key,
            account_id=service_properties.wix_account_id,
            site_id=service_properties.wix_site_id,
            deployment=deployment,
        )
    else:
        crm = NoOpCRM(deployment=deployment)

    apple_oauth_client = AppleOauthClient(
        team_id=service_properties.apple_team_id,
        key_id=service_properties.apple_key_id,
        services_id=service_properties.apple_services_id,
        native_client_id=service_properties.apple_native_client_id or None,
        private_key_pem=service_properties.apple_private_key,
        refresh_token_encryption_key=service_properties.apple_refresh_token_encryption_key,
        realm_codec_registry=realm_codec_registry,
    )

    email_sender = NoOpEmailSender(env=global_properties.env)

    ports = JupiterPorts(
        domain_storage_engine=domain_storage_engine,
        search_storage_engine=search_storage_engine,
        search_indexing_storage_engine=search_indexing_storage_engine,
        crm_indexing_storage_engine=crm_indexing_storage_engine,
        crm=crm,
        email_sender=email_sender,
        location_resolver=NoOpLocationResolver(),
        apple_oauth_client=apple_oauth_client,
    )

    cron_app_form = JupiterWebApiCronForm.build_from_module_root(
        ports,
        global_properties,
        service_properties,
        cron_run_time_provider,
        realm_codec_registry,
        concept_registry,
        invocation_recorder,
        SyncAppleUserDataDoAllUseCase,
        JupiterExceptionHandler,
        service_properties.execution_mode,
        jupiter_webapi_sync_apple_user_data_do_all.exceptions,
    )

    rich_print("=" * 80)
    rich_print("Starting Jupiter WebAPI cron (Sync Apple user data):")
    rich_print(f"  Version: {global_properties.version}")
    rich_print(f"  Universe: {global_properties.universe}")
    rich_print(f"  Environment: {global_properties.env}")
    rich_print(f"  Instance: {global_properties.instance}")
    rich_print(f"  Hosting: {global_properties.universe.hosting}")
    rich_print(f"  Execution mode: {service_properties.execution_mode.value}")
    rich_print("-" * 80)
    rich_print("Component Classes:")
    rich_print(f"  Telemetry: {telemetry.__class__.__name__}")
    rich_print(
        "  Mutation Invocation Storage Engine: "
        f"{mutation_invocation_storage_engine.__class__.__name__}"
    )
    rich_print(f"  Invocation Recorder: {invocation_recorder.__class__.__name__}")
    rich_print(f"  Domain Storage Engine: {domain_storage_engine.__class__.__name__}")
    rich_print(f"  Search Storage Engine: {search_storage_engine.__class__.__name__}")
    rich_print(f"  CRM: {crm.__class__.__name__}")
    rich_print(f"  Email Sender: {email_sender.__class__.__name__}")
    rich_print("=" * 80)

    try:
        await cron_app_form.run(sys.argv)
    finally:
        if service_properties.storage_engine == JupiterWebApiStorageEngine.SQLITE:
            try:
                await sqlite_connection.dispose()
            finally:
                pass
        else:
            try:
                await postgres_connection.dispose()
            finally:
                pass
        try:
            await apple_oauth_client.close()
        finally:
            pass
        try:
            await crm.close()
        finally:
            pass


def sync_main() -> None:
    """Run the main function synchronously."""
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
