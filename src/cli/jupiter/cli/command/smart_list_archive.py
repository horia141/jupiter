"""UseCase for archiving a smart list."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.archive import (
    SmartListArchiveUseCase,
)


class SmartListArchive(LoggedInMutationCommand[SmartListArchiveUseCase]):
    """UseCase for archiving of a smart list."""
