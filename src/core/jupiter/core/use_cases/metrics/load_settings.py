"""Load settings for metrics use case."""
from dataclasses import dataclass

from jupiter.core.domain.projects.project import Project
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class MetricLoadSettingsArgs(UseCaseArgsBase):
    """MetricLoadSettings args."""


@dataclass
class MetricLoadSettingsResult(UseCaseResultBase):
    """MetricLoadSettings results."""

    collection_project: Project


class MetricLoadSettingsUseCase(
    AppLoggedInReadonlyUseCase[MetricLoadSettingsArgs, MetricLoadSettingsResult],
):
    """The command for loading the settings around metrics."""

    async def _execute(
        self,
        context: AppLoggedInUseCaseContext,
        args: MetricLoadSettingsArgs,
    ) -> MetricLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._storage_engine.get_unit_of_work() as uow:
            metric_collection = await uow.metric_collection_repository.load_by_parent(
                workspace.ref_id,
            )
            collection_project = await uow.project_repository.load_by_id(
                metric_collection.collection_project_ref_id,
            )

        return MetricLoadSettingsResult(collection_project=collection_project)
