"""UseCase for changing the default workspace of a project."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import ContextProgressReporter, UseCaseArgsBase
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

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceChangeDefaultProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_updating_entity(
            "workspace",
            workspace.ref_id,
            str(workspace.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                (
                    await uow.project_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )
                project = await uow.project_repository.load_by_id(
                    args.default_project_ref_id,
                )

                workspace = workspace.change_default_project(
                    default_project_ref_id=project.ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                await uow.workspace_repository.save(workspace)
                await entity_reporter.mark_local_change()
