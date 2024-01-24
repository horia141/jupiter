"""UseCase for archiving a smart list tag."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.tag.archive import (
    SmartListTagArchiveUseCase,
)


class SmartListTagArchive(LoggedInMutationCommand[SmartListTagArchiveUseCase]):
    """UseCase for archiving a smart list tag."""
