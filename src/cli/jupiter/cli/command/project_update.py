"""UseCase for creating projects."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.projects.update import (
    ProjectUpdateUseCase,
)


class ProjectUpdate(LoggedInMutationCommand[ProjectUpdateUseCase]):
    """UseCase class for updating projects."""
