"""UseCase for hard removing a smart list."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.remove import (
    SmartListRemoveUseCase,
)


class SmartListsRemove(LoggedInMutationCommand[SmartListRemoveUseCase]):
    """UseCase for hard removing of a smart list."""
