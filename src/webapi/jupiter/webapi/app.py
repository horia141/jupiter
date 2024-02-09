"""The app, part of the framework."""
import abc
import dataclasses
import types
from typing import (
    Annotated,
    Any,
    Callable,
    Final,
    Generic,
    Iterator,
    Mapping,
    TypeVar,
    cast,
    get_args,
)
from jupiter.core.framework.realm import DatabaseRealm, WebRealm

import inflection
from jupiter.core.framework.thing import Thing
from pydantic import BaseModel, create_model, validator
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.storage_engine import DomainStorageEngine, SearchStorageEngine
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.use_case import (
    EmptySession,
    MutationUseCaseInvocationRecorder,
    UseCase,
    UseCaseContextBase,
    UseCaseSessionBase,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, UseCaseResultBase
from jupiter.core.framework.utils import find_all_modules, normalize_optional
from jupiter.core.use_cases.infra.storage_engine import UseCaseStorageEngine
from jupiter.core.use_cases.infra.use_cases import (
    AppBackgroundMutationUseCase,
    AppGuestMutationUseCase,
    AppGuestReadonlyUseCase,
    AppGuestUseCaseSession,
    AppLoggedInMutationUseCase,
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseSession,
)
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.progress_reporter import (
    EmptyProgressReporterFactory,
    NoOpProgressReporterFactory,
)
from jupiter.webapi.time_provider import CronRunTimeProvider, PerRequestTimeProvider
from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory
from starlette.middleware.base import BaseHTTPMiddleware

STANDARD_RESPONSES: dict[int | str, dict[str, Any]] = {
    410: {"description": "Workspace Or User Not Found", "content": {"plain/text": {}}},
    406: {"description": "Feature Not Available", "content": {"plain/text": {}}},
}

STANDARD_CONFIG: Mapping[str, Any] = {
    "responses": STANDARD_RESPONSES,
    "response_model_exclude_defaults": True,
}

oauth2_guest_scheme = OAuth2PasswordBearer(tokenUrl="guest-login", auto_error=False)
oauth2_logged_in_schemea = OAuth2PasswordBearer(tokenUrl="old-skool-login")


def construct_guest_auth_token_ext(
    token_raw: Annotated[str | None, Depends(oauth2_guest_scheme)]
) -> AuthTokenExt | None:
    """Construct a Token from the raw token string."""
    return AuthTokenExt.from_raw(token_raw) if token_raw else None


def construct_logged_in_auth_token_ext(
    token_raw: Annotated[str, Depends(oauth2_logged_in_schemea)]
) -> AuthTokenExt:
    """Construct a Token from the raw token string."""
    return AuthTokenExt.from_raw(token_raw)


def construct_guest_session(
    auth_token_ext: Annotated[
        AuthTokenExt | None, Depends(construct_guest_auth_token_ext)
    ]
) -> AppGuestUseCaseSession:
    """Construct a GuestSession from the AuthTokenExt."""
    return AppGuestUseCaseSession(auth_token_ext)


def construct_logged_in_session(
    auth_token_ext: Annotated[AuthTokenExt, Depends(construct_logged_in_auth_token_ext)]
) -> AppLoggedInUseCaseSession:
    """Construct a LoggedInSession from the AuthTokenExt."""
    return AppLoggedInUseCaseSession(auth_token_ext)


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
    _pydantic_arg_model: type[BaseModel]
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
        self._pydantic_arg_model = self._build_args_model(realm_codec_registry, self._args_type)
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

    @staticmethod
    def _build_args_model(realm_codec_registry: RealmCodecRegistry, the_type: type[UseCaseArgsBase]) -> type[BaseModel]:
        fields = {}
        validators = {}

        for field in dataclasses.fields(the_type):
            real_type, is_optional = normalize_optional(field.type)
            if is_optional:
                fields[field.name] = (field.type, None)
            else:
                fields[field.name] = (field.type, ...)
            field_decoder = realm_codec_registry.get_decoder(field.type, WebRealm)
            validators[field.name] = validator(field.name, pre=True, allow_reuse=True)(lambda cls, v: field_decoder.decode(v))

        model = create_model(the_type.__name__, **fields, __validators__=validators)

        return model

    def _build_http_name(self) -> str:
        return inflection.dasherize(
            inflection.underscore(self._use_case.__class__.__name__)
        ).replace("-use-case", "")

    def _build_api_name(self) -> str:
        return self._use_case.__class__.__name__.replace("UseCase", "")

    def _build_description(self) -> str:
        return self._use_case.__doc__ or ""

    def _build_tag(self) -> str:
        return inflection.dasherize(
            self._use_case.__module__[len(self._root_module.__name__) + 1 :].split(".")[
                0
            ]
        )

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
            response_model=self._result_type,
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(args: self._pydantic_arg_model, session: GuestSession) -> UseCaseResultT:  # type: ignore[name-defined]
            return cast(
                UseCaseResultT, (await self._use_case.execute(session, args))[1]
            )


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
            response_model=self._result_type,
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(args: self._pydantic_arg_model, session: GuestSession) -> UseCaseResultT:  # type: ignore[name-defined]
            return cast(
                UseCaseResultT, (await self._use_case.execute(session, args))[1]
            )


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
            response_model=self._result_type,
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(args: self._pydantic_arg_model, session: LoggedInSession) -> UseCaseResultT:  # type: ignore[name-defined]
            return cast(
                UseCaseResultT, (await self._use_case.execute(session, args))[1]
            )


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
            response_model=self._result_type,
            summary=self._build_description(),
            description=self._build_description(),
            tags=[self._build_tag()],
            **STANDARD_CONFIG,
        )
        async def do_it(args: self._pydantic_arg_model, session: LoggedInSession) -> UseCaseResultT:  # type: ignore[name-defined]
            return cast(
                UseCaseResultT, (await self._use_case.execute(session, args))[1]
            )


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

    def attach_route(self, app: FastAPI) -> None:
        """Attach the route to the app."""
        raise Exception("Cron commands should not be attached to the app.")


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
            openapi_url="/openapi.json"
            if global_properties.env.is_development
            else None,
            docs_url="/docs" if global_properties.env.is_development else None,
            redoc_url="/redoc" if global_properties.env.is_development else None,
        )
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
            use_case_storage_engine,
        )

        for mr in module_root:
            for m in find_all_modules(mr):
                for use_case_type in extract_use_case(m):
                    if use_case_type in app._use_case_commands:
                        continue
                    app._add_use_case_type(use_case_type, mr)

        for use_case, command in app._use_case_commands.items():
            if isinstance(command, CronCommand):
                app._scheduler.add_job(
                    command.execute,
                    id=use_case.__name__,
                    name=use_case.__name__,
                    trigger="cron",
                    day="*",
                    hour="1",
                )
            elif isinstance(command, UseCaseCommand):
                command.attach_route(app.fast_app)
            else:
                raise Exception(f"Unknown command type {command}")

        return app

    async def run(self) -> None:
        """Run the app."""
        self._scheduler.start()

        self._fast_app.add_middleware(
            BaseHTTPMiddleware, dispatch=self._time_provider_middleware
        )

        config = uvicorn.Config(
            self._fast_app, port=self._global_properties.port, log_level="info"
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
                    invocation_recorder=self._invocation_recorder,
                    progress_reporter_factory=NoOpProgressReporterFactory(),
                    global_properties=self._global_properties,
                    auth_token_stamper=self._auth_token_stamper,
                    domain_storage_engine=self._domain_storage_engine,
                    search_storage_engine=self._search_storage_engine,
                ),
                root_module=root_module,
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
                root_module=root_module,
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
                root_module=root_module,
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
                root_module=root_module,
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
                root_module=root_module,
            )
        else:
            pass
            # raise Exception(f"Unsupported use case type {use_case_type}")

        return self
