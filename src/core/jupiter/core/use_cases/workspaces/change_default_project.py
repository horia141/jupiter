"""UseCase for changing the default workspace of a project."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
    use_case_args,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
    mutation_use_case,
)


@use_case_args
class WorkspaceChangeDefaultProjectArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    default_project_ref_id: EntityId


@mutation_use_case()
class WorkspaceChangeDefaultProjectUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceChangeDefaultProjectArgs, None],
):
    """UseCase for changing the default project of a workspace."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkspaceChangeDefaultProjectArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        project = await uow.project_repository.load_by_id(
            args.default_project_ref_id,
        )

        workspace = workspace.change_default_project(
            context.domain_context,
            default_project_ref_id=project.ref_id,
        )

        await uow.workspace_repository.save(workspace)
