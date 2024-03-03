"""The command for updating a project."""

from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_name import ProjectName
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
)
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ProjectUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    ref_id: EntityId
    name: UpdateAction[ProjectName]


@mutation_use_case(WorkspaceFeature.PROJECTS)
class ProjectUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectUpdateArgs, None]
):
    """The command for updating a project."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ProjectUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        project = await uow.get_for(Project).load_by_id(args.ref_id)
        project = project.update(
            ctx=context.domain_context,
            name=args.name,
        )

        await uow.get_for(Project).save(project)
        await progress_reporter.mark_updated(project)
