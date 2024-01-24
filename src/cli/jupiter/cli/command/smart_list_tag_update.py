"""UseCase for updating a smart list tag."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.tag.update import (
    SmartListTagUpdateUseCase,
)


class SmartListTagUpdate(LoggedInMutationCommand[SmartListTagUpdateUseCase]):
    """UseCase for creating a smart list tag."""
