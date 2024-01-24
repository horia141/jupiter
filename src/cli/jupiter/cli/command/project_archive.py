"""UseCase for archiving projects."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.projects.archive import (
    ProjectArchiveUseCase,
)


class ProjectArchive(LoggedInMutationCommand[ProjectArchiveUseCase]):
    """UseCase class for archiving projects."""
