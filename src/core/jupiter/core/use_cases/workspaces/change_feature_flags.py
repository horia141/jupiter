"""Change the workspace feature flags."""
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import WorkspaceFeature
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
class WorkspaceChangeFeatureFlagsArgs(UseCaseArgsBase):
    """WorkspaceChangeFeatureFlags args."""

    feature_flags: set[WorkspaceFeature]


@mutation_use_case()
class WorkspaceChangeFeatureFlagsUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the workspace."""

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
        args: WorkspaceChangeFeatureFlagsArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        _, feature_flags_controls = infer_feature_flag_controls(self._global_properties)
        workspace_feature_flags = {}
        for feature_flag in WorkspaceFeature:
            workspace_feature_flags[feature_flag] = feature_flag in args.feature_flags

        workspace = workspace.change_feature_flags(
            context.domain_context,
            feature_flag_controls=feature_flags_controls,
            feature_flags=workspace_feature_flags,
        )
        await uow.workspace_repository.save(workspace)
