"""Change the user feature flags."""
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
)
from jupiter.core.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
    ProgressReporterFactory,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@use_case_args
class UserChangeFeatureFlagsArgs(UseCaseArgsBase):
    """UserChangeFeatureFlags args."""

    feature_flags: set[UserFeature]


@mutation_use_case()
class UserChangeFeatureFlagsUseCase(
    AppTransactionalLoggedInMutationUseCase[UserChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the user."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[
            AppLoggedInMutationUseCaseContext
        ],
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
        context: AppLoggedInMutationUseCaseContext,
        args: UserChangeFeatureFlagsArgs,
    ) -> None:
        """Execute the command's action."""
        user = context.user
        feature_flags_controls, _ = infer_feature_flag_controls(self._global_properties)
        user_feature_flags = {}
        for feature_flag in UserFeature:
            user_feature_flags[feature_flag] = feature_flag in args.feature_flags

        user = user.change_feature_flags(
            context.domain_context,
            feature_flag_controls=feature_flags_controls,
            feature_flags=user_feature_flags,
        )
        await uow.user_repository.save(user)
