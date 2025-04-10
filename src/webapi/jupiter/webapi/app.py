"""The app, part of the framework."""

import abc
import dataclasses
import types
import typing
from collections.abc import Callable, Iterator, Mapping
from datetime import date, datetime
from typing import (
    Annotated,
    Any,
    Final,
    ForwardRef,
    Generic,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

import inflection
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.types import DecoratedCallable
from jupiter.core.domain.app import (
    AppCore,
    AppDistribution,
    AppPlatform,
    AppShell,
    AppVersion,
)
from jupiter.core.domain.app_version_decoder import AppVersionDatabaseDecoder
from jupiter.core.domain.concept.auth.auth_token_ext import (
    AuthTokenExt,
    AuthTokenExtDatabaseDecoder,
)
from jupiter.core.domain.concept.auth.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.concept.auth.password_plain import PasswordPlain
from jupiter.core.domain.core.email_address import EmailAddress
from jupiter.core.domain.crm import CRM
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.entity import Entity, ParentLink
from jupiter.core.framework.optional import normalize_optional
from jupiter.core.framework.primitive import Primitive
from jupiter.core.framework.realm import DomainThing, RealmCodecRegistry, WebRealm
from jupiter.core.framework.record import Record
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    EmptySession,
    MutationUseCaseInvocationRecorder,
    UseCase,
    UseCaseContextBase,
    UseCaseSessionBase,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.utils import (
    find_all_modules,
    is_primitive_type,
    is_thing_ish_type,
)
from jupiter.core.framework.value import (
    AtomicValue,
    CompositeValue,
    EnumValue,
    SecretValue,
)
from jupiter.core.use_cases.infra.realms import (
    _StandardEnumValueDatabaseDecoder,
)
from jupiter.core.use_cases.infra.storage_engine import UseCaseStorageEngine
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestMutationUseCase,
    AppGuestReadonlyUseCase,
    AppGuestUseCaseSession,
    AppLoggedInMutationUseCase,
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseSession,
    SysBackgroundMutationUseCase,
)
from jupiter.core.use_cases.login import LoginArgs, LoginUseCase
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.progress_reporter import (
    EmptyProgressReporterFactory,
    NoOpProgressReporterFactory,
)
from jupiter.webapi.time_provider import CronRunTimeProvider, PerRequestTimeProvider
from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory
from pendulum.date import Date
from pendulum.datetime import DateTime
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

STANDARD_RESPONSES: dict[int | str, dict[str, Any]] = {
    410: {
        "description": "Workspace Or User Not Found",
        "content": {"application/json": {}},
    },
    406: {"description": "Feature Not Available", "content": {"application/json": {}}},
    422: {"description": "Validation Error", "content": {"application/json": {}}},
}

STANDARD_CONFIG: Mapping[str, Any] = {
    "responses": STANDARD_RESPONSES,
    "response_model_exclude_defaults": True,
}

ENV_HEADER: Final[str] = "X-Jupiter-Env"
HOSTING_HEADER: Final[str] = "X-Jupiter-Hosting"
VERSION_HEADER: Final[str] = "X-Jupiter-Version"
FRONTDOOR_HEADER: Final[str] = "X-Jupiter-FrontDoor"

AUTH_TOKEN_EXT_DECODER = AuthTokenExtDatabaseDecoder()
APP_VERSION_DECODER = AppVersionDatabaseDecoder()
APP_SHELL_DECODER = _StandardEnumValueDatabaseDecoder(AppShell)
APP_PLATFORM_DECODER = _StandardEnumValueDatabaseDecoder(AppPlatform)
APP_DISTRIBUTION_DECODER = _StandardEnumValueDatabaseDecoder(AppDistribution)
OAUTH2_GUEST_SCHEMA = OAuth2PasswordBearer(tokenUrl="guest-login", auto_error=False)
OAUTH2_LOGGED_IN_SCHEMA = OAuth2PasswordBearer(tokenUrl="old-skool-login")


def construct_guest_auth_token_ext(
    token_raw: Annotated[str | None, Depends(OAUTH2_GUEST_SCHEMA)],
) -> AuthTokenExt | None:
    """Construct a Token from the raw token string."""
    return AUTH_TOKEN_EXT_DECODER.decode(token_raw) if token_raw else None


def construct_logged_in_auth_token_ext(
    token_raw: Annotated[str, Depends(OAUTH2_LOGGED_IN_SCHEMA)],
) -> AuthTokenExt:
    """Construct a Token from the raw token string."""
    return AUTH_TOKEN_EXT_DECODER.decode(token_raw)


def construct_guest_session(
    request: Request,
    auth_token_ext: Annotated[
        AuthTokenExt | None, Depends(construct_guest_auth_token_ext)
    ],
) -> AppGuestUseCaseSession:
    """Construct a GuestSession from the AuthTokenExt."""
    frontdoor_raw = request.headers.get(FRONTDOOR_HEADER)
    app_client_version = AppVersion("0.0.1")
    app_shell = AppShell.BROWSER
    app_platform = AppPlatform.DESKTOP_MACOS
    app_distribution = AppDistribution.WEB
    if frontdoor_raw is not None:
        bits = frontdoor_raw.split(":")
        if len(bits) == 4:
            app_client_version = APP_VERSION_DECODER.decode(bits[0])
            app_shell = APP_SHELL_DECODER.decode(bits[1])
            app_platform = APP_PLATFORM_DECODER.decode(bits[2])
            app_distribution = APP_DISTRIBUTION_DECODER.decode(bits[3])
    return AppGuestUseCaseSession.for_webui(
        auth_token_ext, app_client_version, app_shell, app_platform, app_distribution
    )


def construct_logged_in_session(
    request: Request,
    auth_token_ext: Annotated[
        AuthTokenExt, Depends(construct_logged_in_auth_token_ext)
    ],
) -> AppLoggedInUseCaseSession:
    """Construct a LoggedInSession from the AuthTokenExt."""
    frontdoor_raw = request.headers.get(FRONTDOOR_HEADER)
    app_client_version = AppVersion("0.0.1")
    app_shell = AppShell.BROWSER
    app_platform = AppPlatform.DESKTOP_MACOS
    app_distribution = AppDistribution.WEB
    if frontdoor_raw is not None:
        bits = frontdoor_raw.split(":")
        if len(bits) == 4:
            app_client_version = APP_VERSION_DECODER.decode(bits[0])
            app_shell = APP_SHELL_DECODER.decode(bits[1])
            app_platform = APP_PLATFORM_DECODER.decode(bits[2])
            app_distribution = APP_DISTRIBUTION_DECODER.decode(bits[3])

    return AppLoggedInUseCaseSession.for_webui(
        auth_token_ext, app_client_version, app_shell, app_platform, app_distribution
    )


GuestSession = Annotated[AppGuestUseCaseSession, Depends(construct_guest_session)]
LoggedInSession = Annotated[
    AppLoggedInUseCaseSession, Depends(construct_logged_in_session)
]


class Command:
    """The base class for all commands."""


UseCaseT = TypeVar("UseCaseT", bound=UseCase[Any, Any, Any, Any])
UseCaseSessionT = TypeVar("UseCaseSessionT", bound=UseCaseSessionBase)
UseCaseContextT = TypeVar("UseCaseContextT", bound=UseCaseContextBase)
UseCaseArgsT = TypeVar("UseCaseArgsT", bound=UseCaseArgsBase)
UseCaseResultT = TypeVar("UseCaseResultT", bound=UseCaseResultBase | None)


class UseCaseCommand(Generic[UseCaseT], Command, abc.ABC):
    """A command that is a use case."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _args_type: type[UseCaseArgsBase]
    _result_type: type[UseCaseResultBase | None]
    _use_case: UseCaseT
    _root_module: Final[types.ModuleType]

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        use_case: UseCaseT,
        root_module: types.ModuleType,
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._args_type = self._infer_args_class(use_case)
        self._result_type = self._infer_result_class(use_case)
        self._use_case = use_case
        self._root_module = root_module

    @staticmethod
    def _infer_args_class(use_case: UseCaseT) -> type[UseCaseArgsBase]:
        use_case_type = use_case.__class__
        if not hasattr(use_case_type, "__orig_bases__"):
            raise Exception("No args class found")
        for base in use_case_type.__orig_bases__:  # type: ignore
            args = get_args(base)
            if len(args) > 0:
                return cast(type[UseCaseArgsBase], args[0])
        raise Exception("No args class found")

    @staticmethod
    def _infer_result_class(use_case: UseCaseT) -> type[UseCaseResultBase | None]:
        use_case_type = use_case.__class__
        if not hasattr(use_case_type, "__orig_bases__"):
            raise Exception("No result class found")
        for base in use_case_type.__orig_bases__:  # type: ignore
            args = get_args(base)
            if len(args) > 1:
                return cast(type[UseCaseResultBase | None], args[1])
        raise Exception("No result class found")

    def _build_http_name(self) -> str:
        return inflection.dasherize(
            inflection.underscore(self._use_case.__class__.__name__)
        ).replace("-use-case", "")

    def _build_api_name(self) -> str:
        return self._use_case.__class__.__name__.replace("UseCase", "")

    def _build_description(self) -> str:
        return self._use_case.__doc__ or ""

    def _build_tag(self) -> str:
        some_modules = self._use_case.__module__[
            len(self._root_module.__name__) + 1 :
        ].split(".")
        if len(some_modules) == 1:
            the_one_module = some_modules[0]
        else:
            the_one_module = some_modules[-2]
        the_one_tag = inflection.dasherize(the_one_module)
        return the_one_tag

    @abc.abstractmethod
    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""


GuestMutationCommandUseCase = TypeVar(
    "GuestMutationCommandUseCase", bound=AppGuestMutationUseCase[Any, Any]
)


class GuestMutationCommand(
    Generic[GuestMutationCommandUseCase, UseCaseResultT],
    UseCaseCommand[GuestMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which do not require authentication."""

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""

        @app.post(
            f"/{self._build_http_name()}",
            name=self._build_api_name(),
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(request: Request, session: GuestSession):  # type: ignore[no-untyped-def]
            args_decoder = self._realm_codec_registry.get_decoder(
                self._args_type, WebRealm
            )
            decoded_args = args_decoder.decode(await request.json())
            result = cast(
                UseCaseResultT, (await self._use_case.execute(session, decoded_args))[1]
            )
            result_encoder = self._realm_codec_registry.get_encoder(
                self._result_type, WebRealm
            )
            encoded_result = result_encoder.encode(result)
            return encoded_result


GuestReadonlyCommandUseCase = TypeVar(
    "GuestReadonlyCommandUseCase", bound=AppGuestReadonlyUseCase[Any, Any]
)


class GuestReadonlyCommand(
    Generic[GuestReadonlyCommandUseCase, UseCaseResultT],
    UseCaseCommand[GuestReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""

        @app.post(
            f"/{self._build_http_name()}",
            name=self._build_api_name(),
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(request: Request, session: GuestSession):  # type: ignore[no-untyped-def]
            args_decoder = self._realm_codec_registry.get_decoder(
                self._args_type, WebRealm
            )
            decoded_args = args_decoder.decode(await request.json())
            result = cast(
                UseCaseResultT, (await self._use_case.execute(session, decoded_args))[1]
            )
            result_encoder = self._realm_codec_registry.get_encoder(
                self._result_type, WebRealm
            )
            encoded_result = result_encoder.encode(result)
            return encoded_result


LoggedInMutationCommandUseCase = TypeVar(
    "LoggedInMutationCommandUseCase", bound=AppLoggedInMutationUseCase[Any, Any]
)


class LoggedInMutationCommand(
    Generic[LoggedInMutationCommandUseCase, UseCaseResultT],
    UseCaseCommand[LoggedInMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which require authentication."""

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""

        @app.post(
            f"/{self._build_http_name()}",
            name=self._build_api_name(),
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(request: Request, session: LoggedInSession):  # type: ignore[no-untyped-def]
            args_decoder = self._realm_codec_registry.get_decoder(
                self._args_type, WebRealm
            )
            decoded_args = args_decoder.decode(await request.json())
            result = cast(
                UseCaseResultT, (await self._use_case.execute(session, decoded_args))[1]
            )
            result_encoder = self._realm_codec_registry.get_encoder(
                self._result_type, WebRealm
            )
            encoded_result = result_encoder.encode(result)
            return encoded_result


LoggedInReadonlyCommandUseCase = TypeVar(
    "LoggedInReadonlyCommandUseCase", bound=AppLoggedInReadonlyUseCase[Any, Any]
)


class LoggedInReadonlyCommand(
    Generic[LoggedInReadonlyCommandUseCase, UseCaseResultT],
    UseCaseCommand[LoggedInReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""

        @app.post(
            f"/{self._build_http_name()}",
            name=self._build_api_name(),
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(request: Request, session: LoggedInSession):  # type: ignore[no-untyped-def]
            args_decoder = self._realm_codec_registry.get_decoder(
                self._args_type, WebRealm
            )
            decoded_args = args_decoder.decode(await request.json())
            result = cast(
                UseCaseResultT, (await self._use_case.execute(session, decoded_args))[1]
            )
            result_encoder = self._realm_codec_registry.get_encoder(
                self._result_type, WebRealm
            )
            encoded_result = result_encoder.encode(result)
            return encoded_result


BackgroundMutationUseCase = TypeVar(
    "BackgroundMutationUseCase", bound=SysBackgroundMutationUseCase[Any, Any]
)


class CronCommand(
    Generic[BackgroundMutationUseCase, UseCaseResultT],
    UseCaseCommand[BackgroundMutationUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""

    async def execute(self) -> None:
        """Execute the command."""
        await self._use_case.execute(EmptySession(), self._args_type())

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""
        raise Exception("Cron commands should not be attached to the app.")


_ExceptionT = TypeVar("_ExceptionT", bound=Exception)


class WebExceptionHandler(Generic[_ExceptionT], abc.ABC):
    """An exception handler for the web."""

    _exception_type: type[_ExceptionT]

    def __init__(self, exception_type: type[_ExceptionT]) -> None:
        """Constructor."""
        self._exception_type = exception_type

    @abc.abstractmethod
    def handle(
        self, app: "WebServiceApp", exception: _ExceptionT
    ) -> JSONResponse | PlainTextResponse:
        """Handle the exception."""

    def attach_handler(
        self, web_service_app: "WebServiceApp", fast_api: FastAPI
    ) -> None:
        """Attach the route to the app."""

        @fast_api.exception_handler(self._exception_type)
        async def handle_exception(
            request: Request, exc: _ExceptionT
        ) -> JSONResponse | PlainTextResponse:
            return self.handle(web_service_app, exc)


class WebServiceApp:
    """The app."""

    _global_properties: Final[GlobalProperties]
    _request_time_provider: Final[PerRequestTimeProvider]
    _cron_time_provider: Final[CronRunTimeProvider]
    _invocation_recorder: Final[MutationUseCaseInvocationRecorder]
    _progress_reporter_factory: Final[WebsocketProgressReporterFactory]
    _realm_codec_registry: Final[RealmCodecRegistry]
    _auth_token_stamper: Final[AuthTokenStamper]
    _domain_storage_engine: Final[DomainStorageEngine]
    _search_storage_engine: Final[SearchStorageEngine]
    _use_case_storage_engine: Final[UseCaseStorageEngine]
    _crm: Final[CRM]
    _use_case_commands: Final[
        dict[
            type[
                UseCase[
                    UseCaseSessionBase,
                    UseCaseContextBase,
                    UseCaseArgsBase,
                    UseCaseResultBase | None,
                ]
            ],
            Command,
        ]
    ]
    _commands: Final[dict[str, Command]]
    _exception_handlers: Final[dict[type[Exception], WebExceptionHandler[Exception]]]
    _fast_app: Final[FastAPI]
    _scheduler: Final[AsyncIOScheduler]

    def __init__(
        self,
        global_properties: GlobalProperties,
        request_time_provider: PerRequestTimeProvider,
        cron_time_provider: CronRunTimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: WebsocketProgressReporterFactory,
        realm_codec_registry: RealmCodecRegistry,
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
        use_case_storage_engine: UseCaseStorageEngine,
        crm: CRM,
    ) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._request_time_provider = request_time_provider
        self._cron_time_provider = cron_time_provider
        self._invocation_recorder = invocation_recorder
        self._progress_reporter_factory = progress_reporter_factory
        self._realm_codec_registry = realm_codec_registry
        self._auth_token_stamper = auth_token_stamper
        self._domain_storage_engine = domain_storage_engine
        self._search_storage_engine = search_storage_engine
        self._use_case_storage_engine = use_case_storage_engine
        self._crm = crm
        self._use_case_commands = {}
        self._commands = {}
        self._exception_handlers = {}
        self._fast_app = FastAPI(
            generate_unique_id_function=self._custom_generate_unique_id,
            openapi_url=(
                "/openapi.json" if global_properties.env.is_development else None
            ),
            docs_url="/docs" if global_properties.env.is_development else None,
            redoc_url="/redoc" if global_properties.env.is_development else None,
        )
        self._fast_app.openapi = self._custom_openapi  # type: ignore[method-assign]
        self._scheduler = AsyncIOScheduler()

    @staticmethod
    def build_from_module_root(
        global_properties: GlobalProperties,
        request_time_provider: PerRequestTimeProvider,
        cron_run_time_provider: CronRunTimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: WebsocketProgressReporterFactory,
        realm_codec_registry: RealmCodecRegistry,
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
        use_case_storage_engine: UseCaseStorageEngine,
        crm: CRM,
        *module_root: types.ModuleType,
    ) -> "WebServiceApp":
        """Build the app from the module root."""

        def extract_use_case(
            the_module: types.ModuleType,
        ) -> Iterator[
            type[
                UseCase[
                    UseCaseSessionBase,
                    UseCaseContextBase,
                    UseCaseArgsBase,
                    UseCaseResultBase | None,
                ]
            ]
        ]:
            for _name, obj in the_module.__dict__.items():
                origin_obj = get_origin(obj)
                if not (
                    isinstance(obj, type) and issubclass(origin_obj or obj, UseCase)
                ):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:  # type: ignore
                    # This is not a concret type and we can move on
                    continue

                yield obj

        def extract_exception_handler(
            the_module: types.ModuleType,
        ) -> Iterator[tuple[type[Exception], type[WebExceptionHandler[Exception]]]]:
            for _name, obj in the_module.__dict__.items():
                origin_obj = get_origin(obj)
                if not (
                    isinstance(obj, type)
                    and issubclass(origin_obj or obj, WebExceptionHandler)
                    and obj is not WebExceptionHandler
                ):
                    continue

                if obj.__module__ != the_module.__name__:
                    # This is an import, and not a definition!
                    continue

                if not hasattr(obj, "__parameters__") or not hasattr(
                    obj.__parameters__, "__len__"
                ):
                    continue

                if len(obj.__parameters__) > 0:  # type: ignore
                    # This is not a concret type and we can move on
                    continue

                exception_type = get_args(obj.__orig_bases__[0])[0]  # type: ignore

                yield exception_type, obj

        app = WebServiceApp(
            global_properties,
            request_time_provider,
            cron_run_time_provider,
            invocation_recorder,
            progress_reporter_factory,
            realm_codec_registry,
            auth_token_stamper,
            domain_storage_engine,
            search_storage_engine,
            use_case_storage_engine,
            crm=crm,
        )

        login_use_case = LoginUseCase(
            global_properties=global_properties,
            time_provider=request_time_provider,
            realm_codec_registry=realm_codec_registry,
            auth_token_stamper=auth_token_stamper,
            domain_storage_engine=domain_storage_engine,
            search_storage_engine=search_storage_engine,
        )

        @app.fast_app.get("/healthz", status_code=status.HTTP_200_OK)
        async def healthz() -> None:
            """Health check endpoint."""
            return None

        @app.fast_app.post("/old-skool-login", **STANDARD_CONFIG)
        async def old_skool_login(
            form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        ) -> dict[str, str]:
            """Login via OAuth2 password flow and return an auth token."""
            email_address = realm_codec_registry.db_decode(
                EmailAddress, form_data.username, WebRealm
            )
            password = realm_codec_registry.db_decode(
                PasswordPlain, form_data.password, WebRealm
            )

            result = await login_use_case.execute(
                AppGuestUseCaseSession.for_webui(
                    auth_token_ext=None,
                    app_client_version=global_properties.version,
                    app_shell=AppShell.BROWSER,
                    app_platform=AppPlatform.DESKTOP_MACOS,
                    app_distribution=AppDistribution.WEB,
                ),
                LoginArgs(email_address=email_address, password=password),
            )

            return {
                "access_token": result[1].auth_token_ext.auth_token_str,
                "token_type": "bearer",
            }

        for mr in module_root:
            for m in find_all_modules(mr):
                for use_case_type in extract_use_case(m):
                    if use_case_type in app._use_case_commands:
                        continue
                    app._add_use_case_type(use_case_type, mr)

        for idx, (use_case, command) in enumerate(app._use_case_commands.items()):
            if isinstance(command, CronCommand):
                app._scheduler.add_job(
                    command.execute,
                    id=use_case.__name__,
                    name=use_case.__name__,
                    trigger="cron",
                    day="*",
                    hour=str(min(23, idx)),
                )
            elif isinstance(command, UseCaseCommand):
                command.attach_route(app.fast_app)
            else:
                raise Exception(f"Unknown command type {command}")

        for mr in module_root:
            for m in find_all_modules(mr):
                for exception_type, exception_handler in extract_exception_handler(m):
                    if exception_type in app._exception_handlers:
                        continue
                    handler = app._add_exception_handler(
                        exception_type, exception_handler
                    )
                    handler.attach_handler(app, app.fast_app)

        return app

    async def run(self) -> None:
        """Run the app."""
        self._scheduler.start()

        self._fast_app.add_middleware(
            BaseHTTPMiddleware, dispatch=self._time_provider_middleware
        )
        self._fast_app.add_middleware(
            BaseHTTPMiddleware, dispatch=self._setting_middleware
        )

        config = uvicorn.Config(
            self._fast_app,
            host=self._global_properties.host,
            port=self._global_properties.port,
            log_config=None,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    @property
    def fast_app(self) -> FastAPI:
        """Get the FastAPI app."""
        return self._fast_app

    def _custom_generate_unique_id(self, route: APIRoute) -> str:
        """Generate a OpenAPI unique id from just the route name."""
        return f"{route.name}"

    async def _time_provider_middleware(self, request: Request, call_next: DecoratedCallable) -> Callable[[DecoratedCallable], DecoratedCallable]:  # type: ignore
        """Middleware to provide the time provider."""
        self._request_time_provider.set_request_time()
        return await call_next(request)  # type: ignore

    async def _setting_middleware(self, request: Request, call_next: DecoratedCallable) -> Callable[[DecoratedCallable], DecoratedCallable]:  # type: ignore
        """Middleware to provide the version."""
        response = await call_next(request)  # type: ignore
        response.headers[ENV_HEADER] = self._global_properties.env.value
        response.headers[HOSTING_HEADER] = self._global_properties.hosting.value
        response.headers[VERSION_HEADER] = str(self._global_properties.version)
        return response  # type: ignore

    def _add_use_case_type(
        self,
        use_case_type: type[
            UseCase[UseCaseSessionT, UseCaseContextT, UseCaseArgsT, UseCaseResultT]
        ],
        root_module: types.ModuleType,
    ) -> "WebServiceApp":
        if use_case_type in self._use_case_commands:
            raise Exception(f"Use case type {use_case_type} already added")
        if issubclass(use_case_type, AppGuestMutationUseCase):
            self._use_case_commands[use_case_type] = GuestMutationCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    time_provider=self._request_time_provider,
                    realm_codec_registry=self._realm_codec_registry,
                    invocation_recorder=self._invocation_recorder,
                    progress_reporter_factory=NoOpProgressReporterFactory(),
                    global_properties=self._global_properties,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                    crm=self._crm,
                ),
                root_module=root_module,
            )
        elif issubclass(use_case_type, AppGuestReadonlyUseCase):
            self._use_case_commands[use_case_type] = GuestReadonlyCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    global_properties=self._global_properties,
                    time_provider=self._request_time_provider,
                    realm_codec_registry=self._realm_codec_registry,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
                root_module=root_module,
            )
        elif issubclass(use_case_type, AppLoggedInMutationUseCase):
            scoped_to_app = use_case_type.get_scoped_to_app()  # type: ignore
            scoped_to_env = use_case_type.get_scoped_to_env()  # type: ignore
            if scoped_to_app is None or AppCore.WEBUI in scoped_to_app:
                if (
                    scoped_to_env is None
                    or self._global_properties.env in scoped_to_env
                ):
                    self._use_case_commands[use_case_type] = LoggedInMutationCommand(
                        realm_codec_registry=self._realm_codec_registry,
                        use_case=use_case_type(  # type: ignore
                            global_properties=self._global_properties,
                            time_provider=self._request_time_provider,
                            realm_codec_registry=self._realm_codec_registry,
                            invocation_recorder=self._invocation_recorder,
                            progress_reporter_factory=self._progress_reporter_factory,
                            auth_token_stamper=self._auth_token_stamper,
                            domain_storage_engine=self._domain_storage_engine,
                            search_storage_engine=self._search_storage_engine,
                            use_case_storage_engine=self._use_case_storage_engine,
                            crm=self._crm,
                        ),
                        root_module=root_module,
                    )
        elif issubclass(use_case_type, AppLoggedInReadonlyUseCase):
            scoped_to_app = use_case_type.get_scoped_to_app()  # type: ignore
            scoped_to_env = use_case_type.get_scoped_to_env()  # type: ignore
            if scoped_to_app is None or AppCore.WEBUI in scoped_to_app:
                if (
                    scoped_to_env is None
                    or self._global_properties.env in scoped_to_env
                ):
                    self._use_case_commands[use_case_type] = LoggedInReadonlyCommand(
                        realm_codec_registry=self._realm_codec_registry,
                        use_case=use_case_type(  # type: ignore
                            global_properties=self._global_properties,
                            time_provider=self._request_time_provider,
                            realm_codec_registry=self._realm_codec_registry,
                            auth_token_stamper=self._auth_token_stamper,
                            domain_storage_engine=self._domain_storage_engine,
                            search_storage_engine=self._search_storage_engine,
                        ),
                        root_module=root_module,
                    )
        elif issubclass(use_case_type, SysBackgroundMutationUseCase):
            self._use_case_commands[use_case_type] = CronCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    time_provider=self._cron_time_provider,
                    realm_codec_registry=self._realm_codec_registry,
                    progress_reporter_factory=EmptyProgressReporterFactory(),
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                    crm=self._crm,
                ),
                root_module=root_module,
            )
        else:
            pass
            # raise Exception(f"Unsupported use case type {use_case_type}")

        return self

    def _add_exception_handler(
        self,
        exception_type: type[Exception],
        exception_handler: type[WebExceptionHandler[Exception]],
    ) -> WebExceptionHandler[Exception]:
        if exception_type in self._exception_handlers:
            raise Exception(f"Exception type {exception_type} already added")
        handler = exception_handler(exception_type)
        self._exception_handlers[exception_type] = handler
        return handler

    def _custom_openapi(self) -> dict[str, Any]:  # type: ignore
        def build_field_name(
            field: dataclasses.Field[DomainThing],
            field_type: type[DomainThing] | ForwardRef | str | type[ParentLink],
        ) -> str:
            if field_type is ParentLink:
                return f"{field.name}_ref_id"
            else:
                return field.name

        def build_primitive_type(primitive_type: type[Primitive]) -> str:
            if primitive_type is type(None):
                return "null"
            elif primitive_type is bool:
                return "boolean"
            elif primitive_type is int:
                return "integer"
            elif primitive_type is float:
                return "number"
            elif primitive_type is str:
                return "string"
            elif primitive_type is date:
                return "string"
            elif primitive_type is datetime:
                return "string"
            elif primitive_type is Date:
                return "string"
            elif primitive_type is DateTime:
                return "string"
            else:
                raise Exception(f"Invalid primitive type {primitive_type}")

        def build_composite_field(
            field: dataclasses.Field[DomainThing],
            field_type: type[DomainThing] | ForwardRef | str | type[ParentLink],
        ) -> dict[str, Any]:
            if isinstance(field_type, typing._GenericAlias) and field_type.__name__ == "Literal":  # type: ignore
                return {
                    "title": field.name.capitalize(),
                    "enum": field_type.__args__,
                    "type": "string",
                }
            elif isinstance(field_type, ForwardRef):
                raise Exception(
                    f"Invalid forward ref field {field.name} of type {field_type}"
                )
            elif isinstance(field_type, str):
                return {"$ref": f"#/components/schemas/{field_type}"}
            elif field_type is ParentLink:
                return {"title": f"{field.name.capitalize()} RefId", "type": "string"}
            elif is_primitive_type(field_type):
                return {
                    "title": field.name.capitalize(),
                    "type": build_primitive_type(field_type),
                }
            elif is_thing_ish_type(field_type):
                return {"$ref": f"#/components/schemas/{field_type.__name__}"}
            elif (field_type_origin := get_origin(field_type)) is not None:
                if field_type_origin is typing.Union or (
                    isinstance(field_type_origin, type)
                    and issubclass(field_type_origin, types.UnionType)
                ):
                    # field_type_no, is_optional = normalize_optional(field_type)
                    # if is_optional:
                    #     return build_composite_field(field, field_type_no)

                    field_args = cast(
                        list[type[DomainThing] | ForwardRef | str], get_args(field_type)
                    )
                    return {
                        "anyOf": [build_composite_field(field, fa) for fa in field_args]
                    }
                elif field_type_origin is UpdateAction:
                    update_action_type = cast(
                        type[DomainThing] | ForwardRef | str, get_args(field_type)[0]
                    )
                    return {
                        "title": field.name.capitalize(),
                        "type": "object",
                        "required": ["should_change"],
                        "properties": {
                            "should_change": {
                                "title": "Should Change",
                                "type": "boolean",
                            },
                            "value": build_composite_field(field, update_action_type),
                        },
                    }
                elif field_type_origin is list:
                    list_item_type = cast(
                        type[DomainThing] | ForwardRef | str, get_args(field_type)[0]
                    )
                    return {
                        "type": "array",
                        "items": build_composite_field(field, list_item_type),
                    }
                elif field_type_origin is set:
                    list_item_type = cast(
                        type[DomainThing] | ForwardRef | str, get_args(field_type)[0]
                    )
                    return {
                        "type": "array",
                        "items": build_composite_field(field, list_item_type),
                    }
                elif field_type_origin is dict:
                    dict_value_type = cast(
                        type[DomainThing] | ForwardRef | str, get_args(field_type)[1]
                    )
                    return {
                        "type": "object",
                        "additionalProperties": build_composite_field(
                            field, dict_value_type
                        ),
                    }
                else:
                    raise Exception(f"Invalid field {field.name} of type {field_type}")
            else:
                raise Exception(f"Invalid field {field.name} of type {field_type}")

        def build_enum_value_schema(enum_value_type: type[EnumValue]) -> dict[str, Any]:
            return {
                "title": enum_value_type.__name__,
                "description": enum_value_type.__doc__,
                "enum": enum_value_type.get_all_values(),
            }

        def build_atomic_value_schema(
            atomic_value_type: type[AtomicValue[Primitive]],
        ) -> dict[str, Any]:
            return {
                "title": atomic_value_type.__name__,
                "description": atomic_value_type.__doc__,
                "type": build_primitive_type(atomic_value_type.base_type_hack()),
            }

        def build_composite_schema(
            composite_value_type: type[
                CompositeValue | Entity | Record | UseCaseArgsBase | UseCaseResultBase
            ],
        ) -> dict[str, Any]:
            required = [
                build_field_name(f, f.type)
                for f in dataclasses.fields(composite_value_type)
                if f.name != "events"
                and not normalize_optional(cast(type[object], f.type))[1]
            ]
            result: dict[str, None | str | list[str] | dict[str, Any]] = {
                "title": composite_value_type.__name__,
                "description": composite_value_type.__doc__,
                "type": "object",
                "properties": {
                    build_field_name(f, f.type): build_composite_field(f, f.type)
                    for f in dataclasses.fields(composite_value_type)
                    if f.name != "events"
                },
            }
            if len(required) > 0:
                result["required"] = required
            return result

        def build_secret_value_schema(
            secret_value_type: type[SecretValue],
        ) -> dict[str, Any]:
            return {
                "title": secret_value_type.__name__,
                "description": secret_value_type.__doc__,
                "type": "string",
            }

        if self._fast_app.openapi_schema:
            return self._fast_app.openapi_schema
        openapi_schema = get_openapi(
            title="Jupiter Webapi",
            version=str(self._global_properties.version),
            description="Jupiter Webapi",
            routes=self._fast_app.routes,
        )

        # Generate all components

        openapi_schema["components"]["schemas"] = {}

        for enum_value_type in self._realm_codec_registry.get_all_registered_types(
            EnumValue, WebRealm
        ):
            openapi_schema["components"]["schemas"][enum_value_type.__name__] = (
                build_enum_value_schema(enum_value_type)
            )

        for atomic_value_type in self._realm_codec_registry.get_all_registered_types(AtomicValue, WebRealm):  # type: ignore[type-abstract]
            openapi_schema["components"]["schemas"][atomic_value_type.__name__] = (
                build_atomic_value_schema(atomic_value_type)
            )

        for composite_value_type in self._realm_codec_registry.get_all_registered_types(
            CompositeValue, WebRealm
        ):
            openapi_schema["components"]["schemas"][composite_value_type.__name__] = (
                build_composite_schema(composite_value_type)
            )

        for secret_value_type in self._realm_codec_registry.get_all_registered_types(
            SecretValue, WebRealm
        ):
            openapi_schema["components"]["schemas"][secret_value_type.__name__] = (
                build_secret_value_schema(secret_value_type)
            )

        for entity_type in self._realm_codec_registry.get_all_registered_types(
            Entity, WebRealm
        ):
            openapi_schema["components"]["schemas"][entity_type.__name__] = (
                build_composite_schema(entity_type)
            )

        for record_type in self._realm_codec_registry.get_all_registered_types(
            Record, WebRealm
        ):
            openapi_schema["components"]["schemas"][record_type.__name__] = (
                build_composite_schema(record_type)
            )

        for use_case_args_type in self._realm_codec_registry.get_all_registered_types(
            UseCaseArgsBase, WebRealm
        ):
            openapi_schema["components"]["schemas"][use_case_args_type.__name__] = (
                build_composite_schema(use_case_args_type)
            )

        for use_case_result_type in self._realm_codec_registry.get_all_registered_types(
            UseCaseResultBase, WebRealm
        ):
            openapi_schema["components"]["schemas"][use_case_result_type.__name__] = (
                build_composite_schema(use_case_result_type)
            )

        # Link api with components

        for _use_case, command in self._use_case_commands.items():
            if isinstance(command, UseCaseCommand) and not isinstance(
                command, CronCommand
            ):
                openapi_schema["paths"][f"/{command._build_http_name()}"]["post"][
                    "requestBody"
                ] = {
                    "description": "The input data",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{command._args_type.__name__}"
                            }
                        }
                    },
                }

                if command._result_type is not type(None):
                    openapi_schema["paths"][f"/{command._build_http_name()}"]["post"][
                        "responses"
                    ]["200"] = {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{command._result_type.__name__}"
                                }
                            }
                        },
                    }
                else:
                    openapi_schema["paths"][f"/{command._build_http_name()}"]["post"][
                        "responses"
                    ]["200"] = {
                        "description": "Successful response / Empty body",
                    }

        del openapi_schema["paths"]["/healthz"]
        del openapi_schema["paths"]["/old-skool-login"]

        self._fast_app.openapi_schema = openapi_schema
        return self._fast_app.openapi_schema
