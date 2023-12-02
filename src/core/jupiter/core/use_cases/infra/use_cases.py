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
from jupiter.core.domain.features import (
    FeatureUnavailableError,
    UserFeature,
    WorkspaceFeature,
)
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
)
from jupiter.core.domain.user.user import User
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework import use_case
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    EmptyContext,
    EmptySession,
    MutationUseCase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
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
    _domain_storage_engine: Final[DomainStorageEngine]
    _search_storage_engine: Final[SearchStorageEngine]

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return None

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppLoggedInUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, progress_reporter_factory)
        self._auth_token_stamper = auth_token_stamper
        self._domain_storage_engine = domain_storage_engine
        self._search_storage_engine = search_storage_engine

    async def _build_context(
        self, session: AppLoggedInUseCaseSession
    ) -> AppLoggedInUseCaseContext:
        auth_token = self._auth_token_stamper.verify_auth_token_general(
            session.auth_token_ext
        )
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            user = await uow.user_repository.load_by_id(auth_token.user_ref_id)
            user_workspace_link = await uow.user_workspace_link_repository.load_by_user(
                auth_token.user_ref_id
            )
            workspace = await uow.workspace_repository.load_by_id(
                user_workspace_link.workspace_ref_id
            )

            scoped_feature = self.get_scoped_to_feature()
            if scoped_feature is not None:
                if isinstance(scoped_feature, UserFeature):
                    if not user.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(scoped_feature)
                elif isinstance(scoped_feature, WorkspaceFeature):
                    if not workspace.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(scoped_feature)
                else:
                    for feature in scoped_feature:
                        if isinstance(feature, UserFeature):
                            if not user.is_feature_available(feature):
                                raise FeatureUnavailableError(feature)
                        elif isinstance(feature, WorkspaceFeature):
                            if not workspace.is_feature_available(feature):
                                raise FeatureUnavailableError(feature)

            return AppLoggedInUseCaseContext(user, workspace)

    async def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        result = await self._perform_mutation(progress_reporter, context, args)

        # Register all entities that were created/changed/removed with the search index.
        async with self._search_storage_engine.get_unit_of_work() as uow:
            for created_entity in progress_reporter.created_entities:
                await uow.search_repository.create(
                    context.workspace_ref_id, created_entity
                )

            for updated_entity in progress_reporter.updated_entities:
                await uow.search_repository.update(
                    context.workspace_ref_id, updated_entity
                )

            for removed_entity in progress_reporter.removed_entities:
                await uow.search_repository.remove(
                    context.workspace_ref_id, removed_entity
                )

        return result

    @abc.abstractmethod
    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


class AppTransactionalLoggedInMutationUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    AppLoggedInMutationUseCase[UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation for the app transactionally, and assumes a logged-in user."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        async with self._domain_storage_engine.get_unit_of_work() as uow:
            return await self._perform_transactional_mutation(
                uow, progress_reporter, context, args
            )

    @abc.abstractmethod
    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


class AppLoggedInReadonlyUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    ReadonlyUseCase[
        AppLoggedInUseCaseSession, AppLoggedInUseCaseContext, UseCaseArgs, UseCaseResult
    ],
    abc.ABC,
):
    """A command which does some sort of read in the app, and assumes a logged-in user."""

    _auth_token_stamper: Final[AuthTokenStamper]
    _storage_engine: Final[DomainStorageEngine]

    @staticmethod
    def get_scoped_to_feature() -> Iterable[
        UserFeature
    ] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
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
                if isinstance(scoped_feature, UserFeature):
                    if not user.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(scoped_feature)
                elif isinstance(scoped_feature, WorkspaceFeature):
                    if not workspace.is_feature_available(scoped_feature):
                        raise FeatureUnavailableError(scoped_feature)
                else:
                    for feature in scoped_feature:
                        if isinstance(feature, UserFeature):
                            if not user.is_feature_available(feature):
                                raise FeatureUnavailableError(feature)
                        elif isinstance(feature, WorkspaceFeature):
                            if not workspace.is_feature_available(feature):
                                raise FeatureUnavailableError(feature)

            return AppLoggedInUseCaseContext(user, workspace)


class AppTransactionalLoggedInReadOnlyUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    AppLoggedInReadonlyUseCase[UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of transactional read in the app, and assumes a logged-in user."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
        async with self._storage_engine.get_unit_of_work() as uow:
            return await self._perform_transactional_read(uow, context, args)

    @abc.abstractmethod
    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


class AppBackgroundMutationUseCase(
    Generic[UseCaseArgs, UseCaseResult],
    UseCase[EmptySession, EmptyContext, UseCaseArgs, UseCaseResult],
    abc.ABC,
):
    """A command which does some sort of mutation for the app in the background."""

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
            f"Invoking background mutation command {self.__class__.__name__} with args {args}",
        )
        context = await self._build_context(session)
        return await self._execute(context, args)

    @abc.abstractmethod
    async def _execute(
        self,
        context: EmptyContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""


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
        progress_reporter: ProgressReporter,
        context: EmptyContext,
        args: UseCaseArgs,
    ) -> UseCaseResult:
        """Execute the command's action."""
