"""UseCase for updating a workspace."""
from dataclasses import dataclass
from typing import Final

from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.infra.workspace_notion_manager import (
    WorkspaceNotionManager,
)
from jupiter.domain.workspaces.workspace_name import WorkspaceName
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction
from jupiter.framework.use_case import (
    MutationUseCaseInvocationRecorder,
    UseCaseArgsBase,
    ProgressReporter,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.time_provider import TimeProvider


class WorkspaceUpdateUseCase(AppMutationUseCase["WorkspaceUpdateUseCase.Args", None]):
    """UseCase for updating a workspace."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        name: UpdateAction[WorkspaceName]
        timezone: UpdateAction[Timezone]

    _workspace_notion_manager: Final[WorkspaceNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        workspace_notion_manager: WorkspaceNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._workspace_notion_manager = workspace_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with progress_reporter.start_updating_entity(
            "workspace", workspace.ref_id, str(workspace.name)
        ) as entity_reporter:
            with self._storage_engine.get_unit_of_work() as uow:
                workspace = workspace.update(
                    name=args.name,
                    timezone=args.timezone,
                    source=EventSource.CLI,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(workspace.name))

                uow.workspace_repository.save(workspace)
                entity_reporter.mark_local_change()

            notion_workspace = self._workspace_notion_manager.load_workspace(
                workspace.ref_id
            )
            notion_workspace = notion_workspace.join_with_entity(workspace)
            self._workspace_notion_manager.save_workspace(notion_workspace)
            entity_reporter.mark_remote_change()
