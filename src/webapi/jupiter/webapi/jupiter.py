"""The Jupiter Web RPC API."""
import asyncio

import aiohttp
import jupiter.core.domain
import jupiter.core.use_cases
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.journals.infra.journal_repository import (
    JournalExistsForDatePeriodCombinationError,
)
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.user.infra.user_repository import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.repository import EntityNotFoundError
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
from jupiter.core.use_cases.login import (
    InvalidLoginCredentialsError,
)
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.webapi.app import WebServiceApp
from jupiter.webapi.time_provider import CronRunTimeProvider, PerRequestTimeProvider
from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse


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

    domain_storage_engine = SqliteDomainStorageEngine(
        realm_codec_registry, sqlite_connection
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
    )

    @web_app.fast_app.exception_handler(InputValidationError)
    async def input_validation_error_handler(
        _request: Request, exc: InputValidationError
    ) -> JSONResponse:
        """Transform InputValidationErrors from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"{exc}",
                        "type": "value_error.inputvalidationerror",
                    },
                ],
            },
        )

    @web_app.fast_app.exception_handler(FeatureUnavailableError)
    async def feature_unavailable_error_handler(
        _request: Request, exc: FeatureUnavailableError
    ) -> JSONResponse:
        """Transform FeatureUnavailableError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            content=f"{exc}",
        )

    @web_app.fast_app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_error_handler(
        _request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        """Transform UserAlreadyExistsError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"{exc}",
                        "type": "value_error.useralreadyexistserror",
                    },
                ],
            },
        )

    @web_app.fast_app.exception_handler(ExpiredAuthTokenError)
    async def expired_auth_token_error_handler(
        _request: Request, exc: ExpiredAuthTokenError
    ) -> JSONResponse:
        """Transform ExpiredAuthTokenError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            content="Your session seems to be expired",
        )

    @web_app.fast_app.exception_handler(InvalidLoginCredentialsError)
    async def invalid_login_credentials_error_handler(
        _request: Request, exc: InvalidLoginCredentialsError
    ) -> JSONResponse:
        """Transform InvalidLoginCredentialsError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": "User email or password invalid",
                        "type": "value_error.invalidlogincredentialserror",
                    },
                ],
            },
        )

    @web_app.fast_app.exception_handler(ProjectInSignificantUseError)
    async def project_in_significant_use_error_handler(
        _request: Request, exc: ProjectInSignificantUseError
    ) -> JSONResponse:
        """Transform ProjectInSignificantUseError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": [
                    {
                        "loc": [
                            "body",
                        ],
                        "msg": f"Cannot remove because: {exc}",
                        "type": "value_error.projectinsignificantuserror",
                    },
                ],
            },
        )

    @web_app.fast_app.exception_handler(EntityNotFoundError)
    async def leaf_entity_not_found_error_handler(
        _request: Request,
        _exc: EntityNotFoundError,
    ) -> PlainTextResponse:
        """Transform LeafEntityNotFoundError to something that signals clients the entity does not exist."""
        return PlainTextResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="Entity does not exist",
        )

    @web_app.fast_app.exception_handler(InvalidAuthTokenError)
    async def invalid_auth_token_error(
        _request: Request, exc: InvalidAuthTokenError
    ) -> JSONResponse:
        """Transform InvalidAuthTokenError from the core to the same thing FastAPI would do."""
        return JSONResponse(
            status_code=status.HTTP_426_UPGRADE_REQUIRED,
            content="Your session token seems to be busted",
        )

    @web_app.fast_app.exception_handler(UserNotFoundError)
    async def user_not_found_error(
        _request: Request,
        _exc: UserNotFoundError,
    ) -> PlainTextResponse:
        """Transform UserNotFoundError to something that signals clients the app is in a not-ready state."""
        return PlainTextResponse(
            status_code=status.HTTP_410_GONE,
            content="User does not exist",
        )

    @web_app.fast_app.exception_handler(WorkspaceNotFoundError)
    async def workspace_not_found_error_handler(
        _request: Request,
        _exc: WorkspaceNotFoundError,
    ) -> PlainTextResponse:
        """Transform WorkspaceNotFoundErrors to something that signals clients the app is in a not-ready state."""
        return PlainTextResponse(
            status_code=status.HTTP_410_GONE,
            content="Workspace does not exist",
        )

    @web_app.fast_app.exception_handler(JournalExistsForDatePeriodCombinationError)
    async def journal_exists_for_period_and_date_error_handler(
        _request: Request,
        _exc: JournalExistsForDatePeriodCombinationError,
    ) -> PlainTextResponse:
        """Transform JournalExistsForPeriodAndDateError to something that signals clients the app is in a not-ready state."""
        return PlainTextResponse(
            status_code=status.HTTP_409_CONFLICT,
            content="Journal already exists for this date and period combination",
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
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
