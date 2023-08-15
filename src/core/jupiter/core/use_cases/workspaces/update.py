"""UseCase for updating a workspace."""
from dataclasses import dataclass

from jupiter.core.domain.storage_engine import DomainUnitOfWork
from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInUseCaseContext,
    AppTransactionalLoggedInMutationUseCase,
)


@dataclass
class WorkspaceUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: UpdateAction[WorkspaceName]


class WorkspaceUpdateUseCase(
    AppTransactionalLoggedInMutationUseCase[WorkspaceUpdateArgs, None]
):
    """UseCase for updating a workspace."""

    async def _perform_transactional_mutation(
        self,
        uow: DomainUnitOfWork,
        progress_reporter: ProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        workspace = workspace.update(
            name=args.name,
            source=EventSource.CLI,
            modification_time=self._time_provider.get_current_time(),
        )

        await uow.workspace_repository.save(workspace)
