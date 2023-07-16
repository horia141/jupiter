"""Jupiter specific use cases classes."""
import abc
from dataclasses import dataclass
from typing import Final, Generic, Iterable, TypeVar, Union

from jupiter.core.domain.auth.auth_token import (
    AuthToken,
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import Feature, FeatureUnavailableError
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework import use_case
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    EmptyContext,
    EmptySession,
    MutationUseCase,
    MutationUseCaseInvocationRecorder,
    ProgressReporterFactory,
    ReadonlyUseCase,
    UseCase,
    UseCaseArgsBase,
    UseCaseContextBase,
    UseCaseResultBase,
    UseCaseSessionBase,
)
from jupiter.core.utils.time_provider import TimeProvider

UseCaseSession = TypeVar("UseCaseSession", bound=UseCaseSessionBase)
UseCaseContext = TypeVar("UseCaseContext", bound=UseCaseContextBase)
UseCaseArgs = TypeVar("UseCaseArgs", bound=UseCaseArgsBase)
UseCaseResult = TypeVar("UseCaseResult", bound=Union[None, UseCaseResultBase])


@dataclass
class AppGuestUseCaseSession(EmptySession):
    """The application use case session."""

    auth_token_ext: AuthTokenExt | None = None


@dataclass
class AppGuestUseCaseContext(EmptyContext):
    """The applicatin context to use for guest-OK interactions."""

    auth_token: AuthToken | None


class AppGuestMutationUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    MutationUseCase[
        AppGuestUseCaseSession, AppGuestUseCaseContext, UseCaseArgs, UseCaseResult
    ],
    abc.ABC,
):
    """A command which does some sort of mutation for the app, but does not assume a logged-in user."""

    _auth_token_stamper: Final[AuthTokenStamper]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppGuestUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, progress_reporter_factory)
        self._auth_token_stamper = auth_token_stamper
        self._storage_engine = storage_engine

    async def _build_context(
        self, session: AppGuestUseCaseSession
    ) -> AppGuestUseCaseContext:
        """Construct the context for the use case."""
        try:
            auth_token = (
                self._auth_token_stamper.verify_auth_token_general(
                    session.auth_token_ext
                )
                if session.auth_token_ext
                else None
            )
        except (InvalidAuthTokenError, ExpiredAuthTokenError):
            auth_token = None
        return AppGuestUseCaseContext(auth_token)


class AppGuestReadonlyUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    ReadonlyUseCase[
        AppGuestUseCaseSession, AppGuestUseCaseContext, UseCaseArgs, UseCaseResult
    ],
    abc.ABC,
):
    """A query which does not mutate anything, and does not assume a logged-in user."""

    _auth_token_stamper: Final[AuthTokenStamper]
    _storage_engine: Final[DomainStorageEngine]

    def __init__(
        self,
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__()
        self._auth_token_stamper = auth_token_stamper
        self._storage_engine = storage_engine

    async def _build_context(
        self, session: AppGuestUseCaseSession
    ) -> AppGuestUseCaseContext:
        """Construct the context for the use case."""
        try:
            auth_token = (
                self._auth_token_stamper.verify_auth_token_general(
                    session.auth_token_ext
                )
                if session.auth_token_ext
                else None
            )
        except (InvalidAuthTokenError, ExpiredAuthTokenError):
            auth_token = None
        return AppGuestUseCaseContext(auth_token)


@dataclass
class AppLoggedInUseCaseSession(UseCaseSessionBase):
    """The application use case session for logged-in-OK interactions."""

    auth_token_ext: AuthTokenExt


@dataclass
class AppLoggedInUseCaseContext(UseCaseContextBase):
    """The application use case context for logged-in-OK interactions."""

    user: User
    workspace: Workspace

    @property
    def user_ref_id(self) -> EntityId:
        """The user id."""
        return self.user.ref_id

    @property
    def workspace_ref_id(self) -> EntityId:
        """The workspace id."""
        return self.workspace.ref_id


class AppLoggedInMutationUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    MutationUseCase[
        AppLoggedInUseCaseSession, AppLoggedInUseCaseContext, UseCaseArgs, UseCaseResult
    ],
    abc.ABC,
):
    """A command which does some sort of mutation for the app, and assumes a logged-in user."""

    _auth_token_stamper: Final[AuthTokenStamper]
    _storage_engine: Final[DomainStorageEngine]

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        Feature
    ] | Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return None

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppLoggedInUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, progress_reporter_factory)
        self._auth_token_stamper = auth_token_stamper
        self._storage_engine = storage_engine

    async def _build_context(
        self, session: AppLoggedInUseCaseSession
    ) -> AppLoggedInUseCaseContext:
        auth_token = self._auth_token_stamper.verify_auth_token_general(
            session.auth_token_ext
        )
        async with self._storage_engine.get_unit_of_work() as uow:
            user = await uow.user_repository.load_by_id(auth_token.user_ref_id)
            user_workspace_link = await uow.user_workspace_link_repository.load_by_user(
                auth_token.user_ref_id
            )
            workspace = await uow.workspace_repository.load_by_id(
                user_workspace_link.workspace_ref_id
            )

            scoped_feature = self.get_scoped_to_feature()
            if scoped_feature is not None:
                if isinstance(scoped_feature, Feature):
                    if not workspace.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(
                            f"Feature {scoped_feature.value} is not available in this workspace"
                        )
                else:
                    for feature in scoped_feature:
                        if not workspace.is_feature_available(feature):
                            raise FeatureUnavailableError(
                                f"Feature {feature.value} is not available in this workspace"
                            )

            return AppLoggedInUseCaseContext(user, workspace)


class AppLoggedInReadonlyUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    ReadonlyUseCase[
        AppLoggedInUseCaseSession, AppLoggedInUseCaseContext, UseCaseArgs, UseCaseResult
    ],
    abc.ABC,
):
    """A command which does some sort of mutation for the app, and assumes a logged-in user."""

    _auth_token_stamper: Final[AuthTokenStamper]
    _storage_engine: Final[DomainStorageEngine]

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        Feature
    ] | Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return None

    def __init__(
        self, auth_token_stamper: AuthTokenStamper, storage_engine: DomainStorageEngine
    ) -> None:
        """Constructor."""
        super().__init__()
        self._auth_token_stamper = auth_token_stamper
        self._storage_engine = storage_engine

    async def _build_context(
        self, session: AppLoggedInUseCaseSession
    ) -> AppLoggedInUseCaseContext:
        auth_token = self._auth_token_stamper.verify_auth_token_general(
            session.auth_token_ext
        )
        async with self._storage_engine.get_unit_of_work() as uow:
            user = await uow.user_repository.load_by_id(auth_token.user_ref_id)
            user_workspace_link = await uow.user_workspace_link_repository.load_by_user(
                auth_token.user_ref_id
            )
            workspace = await uow.workspace_repository.load_by_id(
                user_workspace_link.workspace_ref_id
            )

            scoped_feature = self.get_scoped_to_feature()
            if scoped_feature is not None:
                if isinstance(scoped_feature, Feature):
                    if not workspace.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(
                            f"Feature {scoped_feature.value} is not available in this workspace"
                        )
                else:
                    for feature in scoped_feature:
                        if not workspace.is_feature_available(feature):
                            raise FeatureUnavailableError(
                                f"Feature {feature.value} is not available in this workspace"
                            )

            return AppLoggedInUseCaseContext(user, workspace)


class AppTestHelperUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    UseCase[EmptySession, EmptyContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of test mutation."""

    _progress_reporter_factory: ProgressReporterFactory[EmptyContext]

    def __init__(
        self, progress_reporter_factory: ProgressReporterFactory[EmptyContext]
    ) -> None:
        """Constructor."""
        self._progress_reporter_factory = progress_reporter_factory

    async def _build_context(self, session: EmptySession) -> EmptyContext:
        """Construct the context for the use case."""
        return EmptyContext()

    async def execute(
        self,
        session: EmptySession,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        # A hacky hack!
        use_case.LOGGER.info(
            f"Invoking test helper command {self.__class__.__name__} with args {args}",
        )
        context = await self._build_context(session)
        progress_reporter = self._progress_reporter_factory.new_reporter(context)
        return await self._execute(progress_reporter, context, args)

    @abc.abstractmethod
    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: EmptyContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
