"""UseCase for removing projects."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.projects.remove import (
    ProjectRemoveUseCase,
)


class ProjectRemove(LoggedInMutationCommand[ProjectRemoveUseCase]):
    """UseCase class for removing projects."""
