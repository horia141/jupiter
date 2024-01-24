"""UseCase for hard removing a smart list tag."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.tag.remove import (
    SmartListTagRemoveUseCase,
)


class SmartListTagRemove(LoggedInMutationCommand[SmartListTagRemoveUseCase]):
    """UseCase for hard removing a smart list tag."""
