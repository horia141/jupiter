"""Change the user feature flags."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import UserFeatureFlags
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
)
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
    ProgressReporterFactory,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class UserChangeFeatureFlagsArgs(UseCaseArgsBase):
    """UserChangeFeatureFlags args."""

    feature_flags: UserFeatureFlags


class UserChangeFeatureFlagsUseCase(
    AppTransactionalLoggedInMutationUseCase[UserChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the user."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppLoggedInUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        domain_storage_engine: DomainStorageEngine,
        search_storage_engine: SearchStorageEngine,
        global_properties: GlobalProperties,
    ) -> None:
        """Constructor."""
        super().__init__(
            time_provider,
            invocation_recorder,
            progress_reporter_factory,
            auth_token_stamper,
            domain_storage_engine,
            search_storage_engine,
        )
        self._global_properties = global_properties

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: UserChangeFeatureFlagsArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        feature_flags_controls, _ = infer_feature_flag_controls(self._global_properties)

        user = user.change_feature_flags(
            feature_flag_controls=feature_flags_controls,
            feature_flags=args.feature_flags,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )
        await uow.user_repository.save(user)
