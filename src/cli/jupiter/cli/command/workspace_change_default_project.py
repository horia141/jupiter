"""UseCase for changing the default project the workspace."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectUseCase,
)


class WorkspaceChangeDefaultProject(
    LoggedInMutationCommand[WorkspaceChangeDefaultProjectUseCase]
):
    """UseCase class for changing the default project of the workspace."""
