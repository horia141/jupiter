"""Change the workspace feature flags."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import (
    DomainUnitOfWork,
)
from jupiter.core.domain.workspaces.workspace import Workspace
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
class WorkspaceChangeFeatureFlagsArgs(UseCaseArgsBase):
    """WorkspaceChangeFeatureFlags args."""

    feature_flags: set[WorkspaceFeature]


@mutation_use_case()
class WorkspaceChangeFeatureFlagsUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the workspace."""

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
        await uow.get_for(Workspace).save(workspace)
