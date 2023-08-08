"""The command for creating a project."""
from dataclasses import dataclass
from typing import Iterable

from jupiter.core.domain.features import Feature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.use_case import (
    ProgressReporter,
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

    async def _perform_mutation(
        self,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: ProjectCreateArgs,
    ) -> ProjectCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        async with self._domain_storage_engine.get_unit_of_work() as uow:
            project_collection = await uow.project_collection_repository.load_by_parent(
                workspace.ref_id,
            )

            new_project = Project.new_project(
                project_collection_ref_id=project_collection.ref_id,
                name=args.name,
                source=EventSource.CLI,
                created_time=self._time_provider.get_current_time(),
            )

            new_project = await uow.project_repository.create(new_project)
            await progress_reporter.mark_created(new_project)

        return ProjectCreateResult(new_project=new_project)
