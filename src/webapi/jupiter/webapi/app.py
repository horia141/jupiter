"""The app, part of the framework."""
import abc
import types
from typing import Any, Final, Generic, Iterator, TypeVar, cast, get_args, Callable
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.types import DecoratedCallable
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.use_case import EmptySession, MutationUseCaseInvocationRecorder, UseCase, UseCaseContextBase, UseCaseSessionBase
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.utils import find_all_modules
from jupiter.core.use_cases.infra.storage_engine import UseCaseStorageEngine
from jupiter.core.use_cases.infra.use_cases import AppBackgroundMutationUseCase, AppGuestMutationUseCase, AppGuestReadonlyUseCase, AppLoggedInMutationUseCase, AppLoggedInReadonlyUseCase
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.progress_reporter import EmptyProgressReporterFactory, NoOpProgressReporterFactory
from jupiter.core.utils.time_provider import TimeProvider
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory
from jupiter.webapi.time_provider import CronRunTimeProvider, PerRequestTimeProvider


class Command(abc.ABC):
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
    _use_case: UseCaseT

    def __init__(
        self,
        realm_codec_registry: RealmCodecRegistry,
        use_case: UseCaseT,
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._args_type = self._infer_args_class(use_case)
        self._use_case = use_case

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
    
GuestMutationCommandUseCase = TypeVar(
    "GuestMutationCommandUseCase", bound=AppGuestMutationUseCase[Any, Any]
)


class GuestMutationCommand(
    Generic[GuestMutationCommandUseCase, UseCaseResultT],
    UseCaseCommand[GuestMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which do not require authentication."""


GuestReadonlyCommandUseCase = TypeVar(
    "GuestReadonlyCommandUseCase", bound=AppGuestReadonlyUseCase[Any, Any]
)


class GuestReadonlyCommand(
    Generic[GuestReadonlyCommandUseCase, UseCaseResultT],
    UseCaseCommand[GuestReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""


LoggedInMutationCommandUseCase = TypeVar(
    "LoggedInMutationCommandUseCase", bound=AppLoggedInMutationUseCase[Any, Any]
)


class LoggedInMutationCommand(
    Generic[LoggedInMutationCommandUseCase, UseCaseResultT],
    UseCaseCommand[LoggedInMutationCommandUseCase],
    abc.ABC,
):
    """Base class for commands which require authentication."""

LoggedInReadonlyCommandUseCase = TypeVar(
    "LoggedInReadonlyCommandUseCase", bound=AppLoggedInReadonlyUseCase[Any, Any]
)


class LoggedInReadonlyCommand(
    Generic[LoggedInReadonlyCommandUseCase, UseCaseResultT],
    UseCaseCommand[LoggedInReadonlyCommandUseCase],
    abc.ABC,
):
    """Base class for commands which just read and present data."""


BackgroundMutationUseCase = TypeVar(
    "BackgroundMutationUseCase", bound=AppBackgroundMutationUseCase[Any, Any]
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
    _use_case_commands: dict[
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
    _commands: dict[str, Command]
    _fast_app: FastAPI

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
        self._use_case_commands = {}
        self._commands = {}
        self._fast_app = FastAPI(
            generate_unique_id_function=self._custom_generate_unique_id,
            openapi_url="/openapi.json" if global_properties.env.is_development else None,
            docs_url="/docs" if global_properties.env.is_development else None,
            redoc_url="/redoc" if global_properties.env.is_development else None,
        )

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
        *module_root: types.ModuleType
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
                if not (isinstance(obj, type) and issubclass(obj, UseCase)):
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
            use_case_storage_engine
        )

        for m in find_all_modules(*module_root):
            for use_case_type in extract_use_case(m):
                if use_case_type in app._use_case_commands:
                    continue
                app._add_use_case_type(use_case_type)

        return app
    
    async def run(self) -> None:
        """Run the app."""
        scheduler = AsyncIOScheduler()

        for use_case, command in self._use_case_commands.items():
            if isinstance(command, CronCommand):
                scheduler.add_job(
                    command.execute,
                    id=use_case.__name__,
                    name=use_case.__name__,
                    trigger="cron",
                    day="*",
                    hour="1",
                )

        scheduler.start()

        self._fast_app.add_middleware(BaseHTTPMiddleware, dispatch=self._time_provider_middleware)
        
        config = uvicorn.Config(self._fast_app, port=self._global_properties.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    
    @property
    def fast_app(self) -> FastAPI:
        """Get the FastAPI app."""
        return self._fast_app

    def _custom_generate_unique_id(self, route: APIRoute) -> str:
        """Generate a OpenAPI unique id from just the route name."""
        return f"{route.name}"
    
    async def _time_provider_middleware(self, request: Request, call_next: DecoratedCallable) -> Callable[[DecoratedCallable], DecoratedCallable]:  # type: ignore  # noqa: E501
        """Middleware to provide the time provider."""
        self._request_time_provider.set_request_time()
        return await call_next(request)     
    
    def _add_use_case_type(
        self,
        use_case_type: type[
            UseCase[UseCaseSessionT, UseCaseContextT, UseCaseArgsT, UseCaseResultT]
        ],
    ) -> "WebServiceApp":
        if use_case_type in self._use_case_commands:
            raise Exception(f"Use case type {use_case_type} already added")
        if issubclass(use_case_type, AppGuestMutationUseCase):
            self._use_case_commands[use_case_type] = GuestMutationCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    time_provider=self._request_time_provider,
                    invocation_recorder=self._invocation_recorder,
                    progress_reporter_factory=NoOpProgressReporterFactory(),
                    global_properties=self._global_properties,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
            )
        elif issubclass(use_case_type, AppGuestReadonlyUseCase):
            self._use_case_commands[use_case_type] = GuestReadonlyCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    global_properties=self._global_properties,
                    time_provider=self._request_time_provider,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
            )
        elif issubclass(use_case_type, AppLoggedInMutationUseCase):
            self._use_case_commands[use_case_type] = LoggedInMutationCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    global_properties=self._global_properties,
                    time_provider=self._request_time_provider,
                    invocation_recorder=self._invocation_recorder,
                    progress_reporter_factory=self._progress_reporter_factory,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                    use_case_storage_engine=self._use_case_storage_engine,
                ),
            )
        elif issubclass(use_case_type, AppLoggedInReadonlyUseCase):
            self._use_case_commands[use_case_type] = LoggedInReadonlyCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    global_properties=self._global_properties,
                    time_provider=self._request_time_provider,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
            )
        elif issubclass(use_case_type, AppBackgroundMutationUseCase):
            self._use_case_commands[use_case_type] = CronCommand(
                realm_codec_registry=self._realm_codec_registry,
                use_case=use_case_type(  # type: ignore
                    time_provider=self._cron_time_provider,
                    progress_reporter_factory=EmptyProgressReporterFactory(),
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
            )
        else:
            pass
            # raise Exception(f"Unsupported use case type {use_case_type}")

        return self
