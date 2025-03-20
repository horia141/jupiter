"""Set a particular feature in the workspace."""

from jupiter.core.domain.concept.workspaces.workspace import Workspace
from jupiter.core.domain.env import Env
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls


@use_case_args
class WorkspaceSetFeatureArgs(UseCaseArgsBase):
    """Arguments for setting a feature in the workspace."""

    feature: WorkspaceFeature
    value: bool


@mutation_use_case(exclude_env=[Env.PRODUCTION])
class WorkspaceSetFeatureUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceSetFeatureArgs, None]
):
    """Set a particular feature in the workspace."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkspaceSetFeatureArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        feature = args.feature
        value = args.value
        _, feature_flag_controls = infer_feature_flag_controls(self._global_properties)

        workspace = workspace.change_feature_flags(
            context.domain_context,
            feature_flag_controls=feature_flag_controls,
            feature_flags={**workspace.feature_flags, feature: value},
        )

        await uow.get_for(Workspace).save(workspace)
