"""UseCase for creating projects."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.projects.create import (
    ProjectCreateUseCase,
)


class ProjectCreate(LoggedInMutationCommand[ProjectCreateUseCase]):
    """UseCase class for creating projects."""
