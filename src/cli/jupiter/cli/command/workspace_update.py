"""UseCase for updating the workspace."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.workspaces.update import (
    WorkspaceUpdateUseCase,
)


class WorkspaceUpdate(LoggedInMutationCommand[WorkspaceUpdateUseCase]):
    """UseCase class for updating the workspace."""
