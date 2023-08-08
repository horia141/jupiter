"""UseCase for changing the default workspace of a project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ProgressReporter, UseCaseArgsBase
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class WorkspaceChangeDefaultProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    default_project_ref_id: EntityId


class WorkspaceChangeDefaultProjectUseCase(
    AppLoggedInMutationUseCase[WorkspaceChangeDefaultProjectArgs, None],
):
    """UseCase for changing the default project of a workspace."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PROJECTS

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceChangeDefaultProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            project = await uow.project_repository.load_by_id(
                args.default_project_ref_id,
            )

            workspace = workspace.change_default_project(
                default_project_ref_id=project.ref_id,
                source=EventSource.CLI,
                modification_time=self._time_provider.get_current_time(),
            )

            await uow.workspace_repository.save(workspace)
