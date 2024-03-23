"""Change the parent project of the project."""
from jupiter.core.domain.features import WorkspaceFeature
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.service.check_cycles_service import (
    ProjectCheckCyclesService,
    ProjectTreeHasCyclesError,
)
from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.use_case import ProgressReporter
from jupiter.core.framework.use_case_io import UseCaseArgsBase, use_case_args
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class ProjectChangeParentArgs(UseCaseArgsBase):
    """Project change parent args."""

    ref_id: EntityId
    parent_project_ref_id: EntityId | None


@mutation_use_case(WorkspaceFeature.PROJECTS)
class ProjectChangeParentUseCase(
    AppTransactionalLoggedInMutationUseCase[ProjectChangeParentArgs, None]
):
    """The command for changing the parent project of a project."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: ProjectChangeParentArgs,
    ) -> None:
        """Execute the command's action."""
        project = await uow.get_for(Project).load_by_id(args.ref_id)
        project = project.change_parent(
            ctx=context.domain_context,
            parent_project_ref_id=args.parent_project_ref_id,
        )

        await uow.get_for(Project).save(project)
        await progress_reporter.mark_updated(project)

        try:
            await ProjectCheckCyclesService().check_for_cycles(uow, project)
        except ProjectTreeHasCyclesError as err:
            raise InputValidationError("The project tree has cycles.") from err
