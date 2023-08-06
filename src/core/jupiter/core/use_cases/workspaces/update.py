"""UseCase for updating a workspace."""
from dataclasses import dataclass

from jupiter.core.domain.workspaces.workspace_name import WorkspaceName
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction
from jupiter.core.framework.use_case import (
    ContextProgressReporter,
    UseCaseArgsBase,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppLoggedInMutationUseCase,
    AppLoggedInUseCaseContext,
)


@dataclass
class WorkspaceUpdateArgs(UseCaseArgsBase):
    """PersonFindArgs."""

    name: UpdateAction[WorkspaceName]


class WorkspaceUpdateUseCase(AppLoggedInMutationUseCase[WorkspaceUpdateArgs, None]):
    """UseCase for updating a workspace."""

    async def _perform_mutation(
        self,
        progress_reporter: ContextProgressReporter,
        context: AppLoggedInUseCaseContext,
        args: WorkspaceUpdateArgs,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        async with progress_reporter.start_updating_entity(
            "workspace",
            workspace.ref_id,
            str(workspace.name),
        ) as entity_reporter:
            async with self._domain_storage_engine.get_unit_of_work() as uow:
                workspace = workspace.update(
                    name=args.name,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                await entity_reporter.mark_known_name(str(workspace.name))

                await uow.workspace_repository.save(workspace)
                await entity_reporter.mark_local_change()
