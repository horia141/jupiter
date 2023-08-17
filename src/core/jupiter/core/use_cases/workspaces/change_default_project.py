"""UseCase for changing the default workspace of a project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class WorkspaceChangeDefaultProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    default_project_ref_id: EntityId


class WorkspaceChangeDefaultProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceChangeDefaultProjectArgs, None],
):
    """UseCase for changing the default project of a workspace."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[WorkspaceFeature] | WorkspaceFeature | None:
        """The feature the use case is scope to."""
        return WorkspaceFeature.PROJECTS

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceChangeDefaultProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        project = await uow.project_repository.load_by_id(
            args.default_project_ref_id,
        )

        workspace = workspace.change_default_project(
            default_project_ref_id=project.ref_id,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.workspace_repository.save(workspace)
