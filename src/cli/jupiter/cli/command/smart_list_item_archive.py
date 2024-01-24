"""UseCase for archiving a smart list item."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.item.archive import (
    SmartListItemArchiveUseCase,
)


class SmartListItemArchive(LoggedInMutationCommand[SmartListItemArchiveUseCase]):
    """UseCase for archiving of a smart list item."""
