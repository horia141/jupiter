"""Change the user feature flags."""

from jupiter.core.domain.features import UserFeature
from jupiter.core.domain.storage_engine import (
    DomainUnitOfWork,
)
from jupiter.core.domain.user.user import User
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class UserChangeFeatureFlagsArgs(UseCaseArgsBase):
    """UserChangeFeatureFlags args."""

    feature_flags: set[UserFeature]


@mutation_use_case()
class UserChangeFeatureFlagsUseCase(
    AppTransactionalLoggedInMutationUseCase[UserChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the user."""

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
        await uow.get_for(User).save(user)
