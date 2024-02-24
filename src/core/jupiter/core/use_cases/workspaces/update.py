"""UseCase for updating a workspace."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
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
class WorkspaceUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: UpdateAction[WorkspaceName]


@mutation_use_case()
class WorkspaceUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceUpdateArgs, None]
):
    """UseCase for updating a workspace."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInMutationUseCaseContext,
        args: WorkspaceUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        workspace = workspace.update(
            context.domain_context,
            name=args.name,
        )

        await uow.repository_for(Workspace).save(workspace)
