"""The command for hard removing a metric."""
from dataclasses import dataclass

from jupiter.core.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricRemoveArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId


class MetricRemoveUseCase(AppLoggedInMutationUseCase[MetricRemoveArgs, None]):
    """The command for removing a metric."""

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: MetricRemoveArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            metric = await uow.metric_repository.load_by_id(
                args.ref_id, allow_archived=True
            )

        await MetricRemoveService(
            self._storage_engine,
        ).execute(progress_reporter, workspace, metric_collection, metric)
