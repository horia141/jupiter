"""The command for creating a project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
    UseCaseResultBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class ProjectCreateArgs(UseCaseArgsBase):
    """Project create args."""

    name: ProjectName


@dataclass
class ProjectCreateResult(UseCaseResultBase):  # type: ignore
    """Project create results."""

    new_project: Project


class ProjectCreateUseCase(
    AppLoggedInMutationUseCase[ProjectCreateArgs, ProjectCreateResult]
):
    """The command for creating a project."""

    @staticmethod
    def get_scoped_to_feature() -> Iterable[Feature] | Feature | None:
        """The feature the use case is scope to."""
        return Feature.PROJECTS

    async def _execute(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ProjectCreateArgs,
    ) -> ProjectCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_creating_entity(
            "project",
            str(args.name),
        ) as entity_reporter:
            async with self._storage_engine.get_unit_of_work() as uow:
                project_collection = (
                    await uow.project_collection_repository.load_by_parent(
                        workspace.ref_id,
                    )
                )

                new_project = Project.new_project(
                    project_collection_ref_id=project_collection.ref_id,
                    name=args.name,
                    source=EventSource.CLI,
                    created_time=self._time_provider.get_current_time(),
                )

                new_project = await uow.project_repository.create(new_project)
                await entity_reporter.mark_known_entity_id(new_project.ref_id)
                await entity_reporter.mark_known_name(str(args.name))
                await entity_reporter.mark_local_change()

        return ProjectCreateResult(new_project=new_project)
