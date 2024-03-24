"""The command for finding workspaces."""

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.use_case_io import (
    UseCaseArgsBase,
    UseCaseResultBase,
    use_case_args,
    use_case_result,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInReadonlyUseCaseContext,
    AppTransactionalLoggedInReadOnlyUseCase,
    readonly_use_case,
)


@use_case_args
class WorkspaceLoadArgs(UseCaseArgsBase):
    """Workspace find args."""


@use_case_result
class WorkspaceLoadResult(UseCaseResultBase):
    """PersonFindResult object."""

    workspace: Workspace


@readonly_use_case()
class WorkspaceLoadUseCase(
    AppTransactionalLoggedInReadOnlyUseCase[WorkspaceLoadArgs, WorkspaceLoadResult]
):
    """The command for loading workspaces."""

    async def _perform_transactional_read(
        self,
        uow: DomainUnitOfWork,
        context: AppLoggedInReadonlyUseCaseContext,
        args: WorkspaceLoadArgs,
    ) -> WorkspaceLoadResult:
        """Execute the command's action."""
        workspace = context.workspace
        return WorkspaceLoadResult(workspace=workspace)
