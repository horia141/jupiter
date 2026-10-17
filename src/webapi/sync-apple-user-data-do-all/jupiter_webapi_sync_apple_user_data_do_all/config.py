"""Configuration for the Sync Apple user data WebAPI cron."""

import abc
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar, Union, cast

from jupiter.core.backend_blend import (
    JupiterCrmBackend,
    JupiterTelemetry,
    JupiterWebApiSearchBackend,
    JupiterWebApiStorageEngine,
)
from jupiter.core.config import (
    JupiterComponentProperties,
    JupiterGlobalProperties,
    JupiterPorts,
    load_config_project_env,
)
from jupiter.framework.appform.cron.appform import Cron
from jupiter.framework.appform.cron.exception import CronExceptionHandler
from jupiter.framework.appform.cron.execution_mode import CronExecutionMode
from jupiter.framework.service_properties import ServiceProperties
from jupiter.framework.sqlalchemy_async_url import normalized_async_sqlalchemy_db_url

_ExceptionT = TypeVar("_ExceptionT", bound=Exception)


@dataclass(frozen=True)
class JupiterWebApiProperties(ServiceProperties):
    """Properties of a Jupiter WebAPI cron process."""

    storage_engine: JupiterWebApiStorageEngine
    telemetry: JupiterTelemetry
    search_backend: JupiterWebApiSearchBackend
    crm_backend: JupiterCrmBackend
    execution_mode: CronExecutionMode
    sqlite_db_url: str
    postgres_db_url: str
    alembic_ini_path: Path
    alembic_migrations_path: Path
    auth_token_secret: str
    sentry_dsn: str
    wix_api_key: str
    wix_account_id: str
    wix_site_id: str
    algolia_app_id: str
    algolia_write_api_key: str
    apple_team_id: str
    apple_key_id: str
    apple_services_id: str
    apple_native_client_id: str
    apple_private_key: str
    apple_refresh_token_encryption_key: str

    @property
    def sync_sqlite_db_url(self) -> str:
        """A safe sync version of the Sqlite DB url."""
        return self.sqlite_db_url.replace("sqlite+aiosqlite", "sqlite+pysqlite")


def build_web_api_properties() -> JupiterWebApiProperties:
    """Build cron service properties from the environment."""

    def find_up_the_dir_tree(partial_path: Union[str, Path]) -> Path:
        last_here = None
        right_here = Path(os.path.relpath(__file__)).parent
        while True:
            if last_here == right_here:
                raise Exception(f"Critical error - missing config file {partial_path}")
            config_file = right_here / partial_path
            if config_file.exists():
                return config_file
            last_here = right_here
            right_here = right_here.parent

    service_config_path = find_up_the_dir_tree("Config.project")
    load_config_project_env(service_config_path)

    sqlite_db_url = normalized_async_sqlalchemy_db_url(
        os.getenv("SQLITE_DB_URL"),
        async_engine_scheme="sqlite+aiosqlite",
        label="SQLite",
    )
    postgres_db_raw = os.getenv("POSTGRES_DB_URL")
    if postgres_db_raw:
        postgres_db_url = normalized_async_sqlalchemy_db_url(
            postgres_db_raw,
            async_engine_scheme="postgresql+asyncpg",
            label="Postgres",
        )
    else:
        postgres_db_url = ""
    alembic_ini_path = Path(cast(str, os.getenv("ALEMBIC_INI_PATH")))
    alembic_migrations_path = Path(cast(str, os.getenv("ALEMBIC_MIGRATIONS_PATH")))
    auth_token_secret = cast(str, os.getenv("AUTH_TOKEN_SECRET"))
    sentry_dsn = cast(str, os.getenv("SENTRY_DSN"))
    wix_api_key = cast(str, os.getenv("WIX_API_KEY"))
    wix_account_id = cast(str, os.getenv("WIX_ACCOUNT_ID"))
    wix_site_id = cast(str, os.getenv("WIX_SITE_ID"))
    algolia_app_id = cast(str, os.getenv("ALGOLIA_APP_ID"))
    algolia_write_api_key = cast(str, os.getenv("ALGOLIA_WRITE_API_KEY"))
    storage_engine = JupiterWebApiStorageEngine(
        cast(str, os.getenv("WEBAPI_STORAGE_ENGINE"))
    )
    telemetry = JupiterTelemetry(cast(str, os.getenv("TELEMETRY")))
    search_backend = JupiterWebApiSearchBackend(cast(str, os.getenv("WEBAPI_SEARCH")))
    crm_backend = JupiterCrmBackend(cast(str, os.getenv("CRM")))
    execution_mode = CronExecutionMode(
        cast(str, os.getenv("WEBAPI_CRON_EXECUTION_MODE"))
    )
    apple_team_id = cast(str, os.getenv("APPLE_TEAM_ID"))
    apple_key_id = cast(str, os.getenv("APPLE_KEY_ID"))
    apple_services_id = cast(str, os.getenv("APPLE_SERVICES_ID"))
    # Sign in with Apple in the app uses the bundle id as its client id.
    apple_native_client_id = cast(str, os.getenv("BUNDLE_ID"))
    apple_private_key = cast(str, os.getenv("APPLE_PRIVATE_KEY"))
    apple_refresh_token_encryption_key = cast(
        str, os.getenv("APPLE_REFRESH_TOKEN_ENCRYPTION_KEY")
    )

    if not alembic_ini_path.is_absolute():
        alembic_ini_path = find_up_the_dir_tree(alembic_ini_path)
    if not alembic_migrations_path.is_absolute():
        alembic_migrations_path = find_up_the_dir_tree(alembic_migrations_path)

    return JupiterWebApiProperties(
        storage_engine=storage_engine,
        telemetry=telemetry,
        search_backend=search_backend,
        crm_backend=crm_backend,
        execution_mode=execution_mode,
        sentry_dsn=sentry_dsn,
        sqlite_db_url=sqlite_db_url,
        postgres_db_url=postgres_db_url,
        alembic_ini_path=alembic_ini_path,
        alembic_migrations_path=alembic_migrations_path,
        auth_token_secret=auth_token_secret,
        wix_api_key=wix_api_key,
        wix_account_id=wix_account_id,
        wix_site_id=wix_site_id,
        algolia_app_id=algolia_app_id,
        algolia_write_api_key=algolia_write_api_key,
        apple_team_id=apple_team_id,
        apple_key_id=apple_key_id,
        apple_services_id=apple_services_id,
        apple_native_client_id=apple_native_client_id,
        apple_private_key=apple_private_key,
        apple_refresh_token_encryption_key=apple_refresh_token_encryption_key,
    )


class JupiterExceptionHandler(
    CronExceptionHandler[JupiterGlobalProperties, JupiterWebApiProperties, _ExceptionT],
    abc.ABC,
    Generic[_ExceptionT],
):
    """A Jupiter cron exception handler."""


class JupiterWebApiCronForm(
    Cron[
        JupiterPorts,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterComponentProperties,
    ]
):
    """A Jupiter WebAPI cron app form."""
