"""The command for doing a garbage collection run."""
from dataclasses import dataclass
from typing import List, Optional

from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.gc.service.gc_service import GCService
from jupiter.core.domain.sync_target import SyncTarget
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class GCDoArgs(UseCaseArgsBase):
    """GCArgs."""

    source: EventSource
    gc_targets: Optional[List[SyncTarget]] = None


class GCDoUseCase(AppLoggedInMutationUseCase[GCDoArgs, None]):
    """The command for doing a garbage collection run."""

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: GCDoArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace
        gc_targets = (
            args.gc_targets
            if args.gc_targets is not None
            else workspace.infer_sync_targets_for_enabled_features(None)
        )

        gc_targets_diff = list(
            set(gc_targets).difference(
                workspace.infer_sync_targets_for_enabled_features(gc_targets)
            )
        )
        if len(gc_targets_diff) > 0:
            raise FeatureUnavailableError(
                f"GC targets {','.join(s.value for s in gc_targets_diff)} are not supported in this workspace"
            )

        gc_service = GCService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            domain_storage_engine=self._domain_storage_engine,
        )

        await gc_service.do_it(progress_reporter, workspace, gc_targets)
