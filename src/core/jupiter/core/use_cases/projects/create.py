"""The command for creating a project."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ProjectCreateArgs(UseCaseArgsBase):
    """Project create args."""

    name: ProjectName


@use_case_result
class ProjectCreateResult(UseCaseResultBase):  # type: ignore
    """Project create results."""

    new_project: Project


@mutation_use_case(WorkspaceFeature.PROJECTS)
class ProjectCreateUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectCreateArgs, ProjectCreateResult]
):
    """The command for creating a project."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ProjectCreateArgs,
    ) -> ProjectCreateResult:
        """Execute the command's action."""
        workspace = context.workspace

        project_collection = await uow.repository_for(ProjectCollection).load_by_parent(
            workspace.ref_id,
        )

        new_project = Project.new_project(
            ctx=context.domain_context,
            project_collection_ref_id=project_collection.ref_id,
            name=args.name,
        )

        new_project = await uow.repository_for(Project).create(new_project)
        await progress_reporter.mark_created(new_project)

        return ProjectCreateResult(new_project=new_project)
