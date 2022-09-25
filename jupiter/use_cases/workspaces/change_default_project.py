"""UseCase for changing the default workspace of a project."""
from dataclasses import dataclass

from jupiter.domain.projects.project_key import ProjectKey
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, ProgressReporter
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)


class WorkspaceChangeDefaultProjectUseCase(
    AppMutationUseCase["WorkspaceChangeDefaultProjectUseCase.Args", None]
):
    """UseCase for changing the default project of a workspace."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        default_project_key: ProjectKey

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with progress_reporter.start_updating_entity(
            "workspace", workspace.ref_id, str(workspace.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                project_collection = uow.project_collection_repository.load_by_parent(
                    workspace.ref_id
                )
                project = uow.project_repository.load_by_key(
                    project_collection.ref_id, args.default_project_key
                )

                workspace = workspace.change_default_project(
                    default_project_ref_id=project.ref_id,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )

                uow.workspace_repository.save(workspace)
                entity_reporter.mark_local_change()
