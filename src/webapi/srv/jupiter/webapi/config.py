"""Configuration for the WebAPI app."""

import abc
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Generic, TypeVar, Union, cast

from fastapi import HTTPException, Request, Response
from jupiter.core.app import (
    AppCore,
    AppDistribution,
    AppPlatform,
    AppShell,
    AppVersion,
)
from jupiter.core.app_version_decoder import AppVersionDatabaseDecoder
from jupiter.core.application.use_case.login_local import (
    LoginLocalArgs,
    LoginLocalUseCase,
)
from jupiter.core.auth.sub.local.password_plain import PasswordPlainWebDecoder
from jupiter.core.backend_blend import (
    JupiterCrmBackend,
    JupiterTelemetry,
    JupiterWebApiEmailSender,
    JupiterWebApiSearchBackend,
    JupiterWebApiStorageEngine,
)
from jupiter.core.common.email_address import EmailAddress, EmailAddressDatabaseDecoder
from jupiter.core.config import (
    JupiterComponentProperties,
    JupiterGlobalProperties,
    JupiterGuestMutationContext,
    JupiterGuestMutationUseCase,
    JupiterGuestReadonlyContext,
    JupiterGuestReadonlyUseCase,
    JupiterGuestSession,
    JupiterLoggedInMutationContext,
    JupiterLoggedInMutationUseCase,
    JupiterLoggedInReadonlyContext,
    JupiterLoggedInReadonlyUseCase,
    JupiterLoggedInSession,
    JupiterPorts,
    load_config_project_env,
)
from jupiter.framework.appform.webapi.appform import WebApiAppForm
from jupiter.framework.appform.webapi.commands import (
    GuestMutationCommand,
    GuestReadonlyCommand,
    LoggedInMutationCommand,
    LoggedInReadonlyCommand,
)
from jupiter.framework.appform.webapi.exception import WebApiExceptionHandler
from jupiter.framework.auth.auth_token_ext import (
    AuthTokenExt,
    AuthTokenExtDatabaseDecoder,
)
from jupiter.framework.base.trace_id import TraceId, TraceIdDatabaseDecoder
from jupiter.framework.realm.standard import (
    _StandardEnumValueDatabaseDecoder,
)
from jupiter.framework.service_properties import ServiceProperties
from jupiter.framework.sqlalchemy_async_url import normalized_async_sqlalchemy_db_url
from jupiter.framework.use_case_io import UseCaseResultBase
from starlette.status import HTTP_401_UNAUTHORIZED

UNIVERSE_HEADER: Final[str] = "X-Jupiter-Universe"
ENV_HEADER: Final[str] = "X-Jupiter-Env"
INSTANCE_HEADER: Final[str] = "X-Jupiter-Instance"
HOSTING_HEADER: Final[str] = "X-Jupiter-Hosting"
VERSION_HEADER: Final[str] = "X-Jupiter-Version"
FRONTDOOR_HEADER: Final[str] = "X-Jupiter-FrontDoor"
TRACE_ID_HEADER: Final[str] = "X-Jupiter-Trace-Id"

_AUTH_TOKEN_EXT_DECODER = AuthTokenExtDatabaseDecoder()
_APP_VERSION_DECODER = AppVersionDatabaseDecoder()
_APP_SHELL_DECODER = _StandardEnumValueDatabaseDecoder(AppShell)
_APP_PLATFORM_DECODER = _StandardEnumValueDatabaseDecoder(AppPlatform)
_APP_DISTRIBUTION_DECODER = _StandardEnumValueDatabaseDecoder(AppDistribution)
_TRACE_ID_DECODER = TraceIdDatabaseDecoder()


_JupiterGuestMutationUseCaseT = TypeVar("_JupiterGuestMutationUseCaseT", bound=JupiterGuestMutationUseCase[object, object])  # type: ignore
_JupiterGuestReadonlyUseCaseT = TypeVar("_JupiterGuestReadonlyUseCaseT", bound=JupiterGuestReadonlyUseCase[object, object])  # type: ignore
_JupiterLoggedInMutationUseCaseT = TypeVar("_JupiterLoggedInMutationUseCaseT", bound=JupiterLoggedInMutationUseCase[object, object])  # type: ignore
_JupiterLoggedInReadonlyUseCaseT = TypeVar("_JupiterLoggedInReadonlyUseCaseT", bound=JupiterLoggedInReadonlyUseCase[object, object])  # type: ignore
_UseCaseResultT = TypeVar("_UseCaseResultT", bound=Union[None, UseCaseResultBase])
_ExceptionT = TypeVar("_ExceptionT", bound=Exception)


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class JupiterWebApiProperties(ServiceProperties):
    """Properties of the Jupiter Web API."""

    host: str
    port: int
    docs_init_workspace_url: str
    storage_engine: JupiterWebApiStorageEngine
    telemetry: JupiterTelemetry
    search_backend: JupiterWebApiSearchBackend
    crm_backend: JupiterCrmBackend
    email_sender_backend: JupiterWebApiEmailSender
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
    google_client_id: str
    google_client_secret: str
    google_refresh_token_encryption_key: str
    apple_team_id: str
    apple_key_id: str
    apple_services_id: str
    apple_native_client_id: str
    apple_private_key: str
    apple_refresh_token_encryption_key: str
    resend_api_key: str
    resend_from_email: EmailAddress
    google_maps_api_key: str

    @property
    def sync_sqlite_db_url(self) -> str:
        """A safe sync version of the Sqlite DB url."""
        # Bit of implicit knowledge here.
        return self.sqlite_db_url.replace("sqlite+aiosqlite", "sqlite+pysqlite")


def build_web_api_properties() -> JupiterWebApiProperties:
    """Build the web api properties from the environment."""

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

    host = cast(str, os.getenv("HOST"))
    port = int(cast(str, os.getenv("PORT")))
    docs_init_workspace_url = cast(str, os.getenv("DOCS_INIT_WORKSPACE_URL"))
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
    email_sender_backend = JupiterWebApiEmailSender(
        cast(str, os.getenv("WEBAPI_EMAIL_SENDER", "noop"))
    )
    google_client_id = cast(str, os.getenv("GOOGLE_CLIENT_ID"))
    google_client_secret = cast(str, os.getenv("GOOGLE_CLIENT_SECRET"))
    google_refresh_token_encryption_key = cast(
        str, os.getenv("GOOGLE_REFRESH_TOKEN_ENCRYPTION_KEY")
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
    resend_api_key = cast(str, os.getenv("RESEND_API_KEY", ""))
    resend_from_email = EmailAddress(cast(str, os.getenv("RESEND_FROM_EMAIL", "")))
    google_maps_api_key = cast(str, os.getenv("GOOGLE_MAPS_API_KEY", ""))

    if not alembic_ini_path.is_absolute():
        alembic_ini_path = find_up_the_dir_tree(alembic_ini_path)
    if not alembic_migrations_path.is_absolute():
        alembic_migrations_path = find_up_the_dir_tree(alembic_migrations_path)

    return JupiterWebApiProperties(
        host=host,
        port=port,
        docs_init_workspace_url=docs_init_workspace_url,
        storage_engine=storage_engine,
        telemetry=telemetry,
        search_backend=search_backend,
        crm_backend=crm_backend,
        email_sender_backend=email_sender_backend,
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
        google_client_id=google_client_id,
        google_client_secret=google_client_secret,
        google_refresh_token_encryption_key=google_refresh_token_encryption_key,
        apple_team_id=apple_team_id,
        apple_key_id=apple_key_id,
        apple_services_id=apple_services_id,
        apple_native_client_id=apple_native_client_id,
        apple_private_key=apple_private_key,
        apple_refresh_token_encryption_key=apple_refresh_token_encryption_key,
        resend_api_key=resend_api_key,
        resend_from_email=resend_from_email,
        google_maps_api_key=google_maps_api_key,
    )


class JupiterGuestMutationCommand(
    GuestMutationCommand[
        _JupiterGuestMutationUseCaseT,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterGuestSession,
        JupiterGuestMutationContext,
        _UseCaseResultT,
    ],
    Generic[_JupiterGuestMutationUseCaseT, _UseCaseResultT],
):
    """A guest mutation commmand tailore to Jupiter."""

    def _build_session(self, request: Request) -> JupiterGuestSession:
        """Build the session."""
        # extract auth token from the "Authorization" header,
        auth_token_ext_str = _extract_auth_token_ext(request)
        trace_id = _extract_trace_id(request)
        app_component = _extract_component_from_frontdoor(request)

        return JupiterGuestSession(
            app_component,
            trace_id,
            auth_token_ext_str,
        )


class JupiterGuestReadonlyCommand(
    GuestReadonlyCommand[
        _JupiterGuestReadonlyUseCaseT,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterGuestSession,
        JupiterGuestReadonlyContext,
        _UseCaseResultT,
    ],
    Generic[_JupiterGuestReadonlyUseCaseT, _UseCaseResultT],
):
    """A guest readonly command tailore to Jupiter."""

    def _build_session(self, request: Request) -> JupiterGuestSession:
        """Build the session."""
        # extract auth token from the "Authorization" header,
        auth_token_ext_str = _extract_auth_token_ext(request)
        trace_id = _extract_trace_id(request)
        app_component = _extract_component_from_frontdoor(request)

        return JupiterGuestSession(
            app_component,
            trace_id,
            auth_token_ext_str,
        )


class JupiterLoggedInMutationCommand(
    LoggedInMutationCommand[
        _JupiterLoggedInMutationUseCaseT,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterLoggedInSession,
        JupiterLoggedInMutationContext,
        _UseCaseResultT,
    ],
    Generic[_JupiterLoggedInMutationUseCaseT, _UseCaseResultT],
):
    """A logged in mutation command tailore to Jupiter."""

    def _build_session(self, request: Request) -> JupiterLoggedInSession:
        """Build the session."""
        # extract auth token from the "Authorization" header,
        auth_token_ext_str = _extract_auth_token_ext(request)
        trace_id = _extract_trace_id(request)
        if auth_token_ext_str is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        app_component = _extract_component_from_frontdoor(request)

        return JupiterLoggedInSession(
            app_component,
            trace_id,
            auth_token_ext_str,
        )


class JupiterLoggedInReadonlyCommand(
    LoggedInReadonlyCommand[
        _JupiterLoggedInReadonlyUseCaseT,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterLoggedInSession,
        JupiterLoggedInReadonlyContext,
        _UseCaseResultT,
    ],
    Generic[_JupiterLoggedInReadonlyUseCaseT, _UseCaseResultT],
):
    """A logged in readonly command tailore to Jupiter."""

    def _build_session(self, request: Request) -> JupiterLoggedInSession:
        """Build the session."""
        # extract auth token from the "Authorization" header,
        auth_token_ext_str = _extract_auth_token_ext(request)
        trace_id = _extract_trace_id(request)
        if auth_token_ext_str is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        app_component = _extract_component_from_frontdoor(request)

        return JupiterLoggedInSession(
            app_component,
            trace_id,
            auth_token_ext_str,
        )


class JupiterExceptionHandler(
    WebApiExceptionHandler[
        JupiterGlobalProperties, JupiterWebApiProperties, _ExceptionT
    ],
    abc.ABC,
    Generic[_ExceptionT],
):
    """A Jupiter exception handler."""

    def on_exception(self, exc: _ExceptionT) -> None:
        """Log handled exceptions in non-production environments."""
        if self._global_properties.env.is_development:
            LOGGER.error(
                "WebAPI exception %s: %s",
                self._exception_type.__name__,
                exc,
                exc_info=exc,
            )


class JupiterWebApiAppForm(
    WebApiAppForm[
        JupiterPorts,
        JupiterGlobalProperties,
        JupiterWebApiProperties,
        JupiterComponentProperties,
    ]
):
    """A Jupiter web api app form."""

    @property
    def api_description(self) -> str:
        """The description of the app."""
        return self._global_properties.description

    @property
    def api_version(self) -> str:
        """The version of the app."""
        return str(self._global_properties.version)

    @property
    def host(self) -> str:
        """The host of the app."""
        return self._service_properties.host

    @property
    def port(self) -> int:
        """The port of the app."""
        return self._service_properties.port

    @property
    def is_live(self) -> bool:
        """Whether the app is live."""
        return self._global_properties.env.is_live

    @property
    def healthz_route(self) -> str:
        """The healthz URL of the app."""
        return "/healthz"

    @property
    def simple_login_route(self) -> str:
        """The simple login route of the app."""
        return "/simple-login"

    @property
    def openapi_json_route(self) -> str:
        """The openapi json route of the app."""
        return "/openapi.json"

    @property
    def openapi_docs_route(self) -> str:
        """The openapi docs route of the app."""
        return "/docs"

    @property
    def openapi_redoc_route(self) -> str:
        """The redoc route of the app."""
        return "/redoc"

    def add_headers_to_response(self, response: Response) -> None:
        """Add the headers to the response."""
        response.headers[UNIVERSE_HEADER] = str(self._global_properties.universe)
        response.headers[ENV_HEADER] = self._global_properties.env.value
        response.headers[INSTANCE_HEADER] = str(self._global_properties.instance)
        response.headers[HOSTING_HEADER] = (
            self._global_properties.universe.hosting.value
        )
        response.headers[VERSION_HEADER] = self.api_version

    async def simple_login(
        self, email_address_raw: str, password_raw: str
    ) -> dict[str, str]:
        """Simple login endpoint."""
        email_address = EmailAddressDatabaseDecoder().decode(email_address_raw)
        password = PasswordPlainWebDecoder().decode(password_raw)

        login_use_case = LoginLocalUseCase(
            global_properties=self._global_properties,
            time_provider=self._request_time_provider,
            realm_codec_registry=self._realm_codec_registry,
            concept_registry=self._concept_registry,
            auth_token_stamper=self._auth_token_stamper,
            invocation_recorder=self._invocation_recorder,
            ports=self._ports,
        )

        result = await login_use_case.execute(
            JupiterGuestSession(
                component_properties=JupiterComponentProperties.for_app(
                    core=AppCore.WEBUI,
                    the_shell=AppShell.BROWSER,
                    platform=AppPlatform.DESKTOP_MACOS,
                    distribution=AppDistribution.WEB,
                    version=self._global_properties.version,
                ),
                trace_id=TraceId.new(),
                auth_token_ext=None,
            ),
            LoginLocalArgs(email_address=email_address, password=password),
        )

        return {
            "access_token": result[1].auth_token_ext.auth_token_str,
            "token_type": "bearer",  # nosec B105
        }


def _extract_auth_token_ext(request: Request) -> AuthTokenExt | None:
    """Extract the auth token ext from the request."""
    authorization_header = request.headers.get("Authorization")
    if authorization_header is None:
        return None
    scheme, _, param = authorization_header.partition(" ")
    if scheme.lower() != "bearer":
        return None
    return _AUTH_TOKEN_EXT_DECODER.decode(param)


def _extract_trace_id(request: Request) -> TraceId:
    """Extract the trace id from the request."""
    trace_id_header = request.headers.get(TRACE_ID_HEADER)
    if trace_id_header is None:
        return TraceId.new()
    return _TRACE_ID_DECODER.decode(trace_id_header)


def _extract_component_from_frontdoor(request: Request) -> JupiterComponentProperties:
    """Extract the app component from the frontdoor."""
    frontdoor_raw = request.headers.get(FRONTDOOR_HEADER)
    app_client_version = AppVersion("0.0.1")
    app_shell = AppShell.BROWSER
    app_platform = AppPlatform.DESKTOP_MACOS
    app_distribution = AppDistribution.WEB
    if frontdoor_raw is not None:
        bits = frontdoor_raw.split(":")
        if len(bits) == 4:
            app_client_version = _APP_VERSION_DECODER.decode(bits[0])
            app_shell = _APP_SHELL_DECODER.decode(bits[1])
            app_platform = _APP_PLATFORM_DECODER.decode(bits[2])
            app_distribution = _APP_DISTRIBUTION_DECODER.decode(bits[3])
    return JupiterComponentProperties.for_app(
        core=_infer_app_core_from_shell(app_shell),
        the_shell=app_shell,
        platform=app_platform,
        distribution=app_distribution,
        version=app_client_version,
    )


def _infer_app_core_from_shell(app_shell: AppShell) -> AppCore:
    """Infer the AppCore from the AppShell value."""
    if app_shell == AppShell.API:
        return AppCore.API
    elif app_shell == AppShell.CLI:
        return AppCore.CLI
    else:
        return AppCore.WEBUI
