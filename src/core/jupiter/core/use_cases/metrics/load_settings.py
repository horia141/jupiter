"""Load settings for metrics use case."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import UserFeature, WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
)


@dataclass
class MetricLoadSettingsArgs(UseCaseArgsBase):
    """MetricLoadSettings args."""


@dataclass
class MetricLoadSettingsResult(UseCaseResultBase):
    """MetricLoadSettings results."""

    collection_project: Project


class MetricLoadSettingsUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[
        MetricLoadSettingsArgs, MetricLoadSettingsResult
    ],
):
    """The command for loading the settings around metrics."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[UserFeature] | UserFeature | Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.METRICS

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInUseCaseContext,
        args: MetricLoadSettingsArgs,
    ) -> MetricLoadSettingsResult:
        """Execute the command's action."""
        workspace = context.workspace

        metric_collection = await uow.metric_collection_repository.load_by_parent(
            workspace.ref_id,
        )
        collection_project = await uow.project_repository.load_by_id(
            metric_collection.collection_project_ref_id,
        )

        return MetricLoadSettingsResult(collection_project=collection_project)
