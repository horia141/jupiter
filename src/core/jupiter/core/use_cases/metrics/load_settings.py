"""Load settings for metrics use case."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class MetricLoadSettingsArgs(UseCaseArgsBase):
    """MetricLoadSettings args."""


@use_case_result
class MetricLoadSettingsResult(UseCaseResultBase):
    """MetricLoadSettings results."""

    collection_project: Project


@readonly_use_case(WorkspaceFeature.METRICS, exclude_app=[EventSource.CLI])
class MetricLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        MetricLoadSettingsArgs, MetricLoadSettingsResult
    ],
):
    """The command for loading the settings around metrics."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: MetricLoadSettingsArgs,
    ) -> MetricLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.repository_for(MetricCollection).load_by_parent(
            workspace.ref_id,
        )
        collection_project = await uow.repository_for(Project).load_by_id(
            metric_collection.collection_project_ref_id,
        )

        return MetricLoadSettingsResult(collection_project=collection_project)
