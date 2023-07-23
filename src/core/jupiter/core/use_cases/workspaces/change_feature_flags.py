"""Change the workspace feature flags."""
from dataclasses import dataclass
from typing import Final

from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import FeatureFlags
from jupiter.core.domain.storage_engine import DomainStorageEngine
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    MutationUseCaseInvocationRecorder,
    ProgressReporterFactory,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)
from jupiter.core.utils.feature_flag_controls import infer_feature_flag_controls
from jupiter.core.utils.global_properties import GlobalProperties
from jupiter.core.utils.time_provider import TimeProvider


@dataclass
class WorkspaceChangeFeatureFlagsArgs(UseCaseArgsBase):
    """WorkspaceChangeFeatureFlags args."""

    feature_flags: FeatureFlags


class WorkspaceChangeFeatureFlagsUseCase(
    AppLoggedInMutationUseCase[WorkspaceChangeFeatureFlagsArgs, None]
):
    """Usecase for changing the feature flags for the workspace."""

    _global_properties: Final[GlobalProperties]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        progress_reporter_factory: ProgressReporterFactory[AppLoggedInUseCaseContext],
        auth_token_stamper: AuthTokenStamper,
        storage_engine: DomainStorageEngine,
        global_properties: GlobalProperties,
    ) -> None:
        """Constructor."""
        super().__init__(
            time_provider,
            invocation_recorder,
            progress_reporter_factory,
            auth_token_stamper,
            storage_engine,
        )
        self._global_properties = global_properties

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceChangeFeatureFlagsArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        feature_flags_controls = infer_feature_flag_controls(self._global_properties)

        async with progress_reporter.start_updating_entity(
            "workspace",
            workspace.ref_id,
            str(workspace.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                workspace = workspace.change_feature_flags(
                    feature_flag_controls=feature_flags_controls,
                    feature_flags=args.feature_flags,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await uow.workspace_repository.save(workspace)
                await entity_reporter.mark_local_change()
