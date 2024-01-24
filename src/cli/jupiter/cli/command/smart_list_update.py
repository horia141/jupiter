"""UseCase for updating a smart list."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.update import (
    SmartListUpdateUseCase,
)


class SmartListUpdate(LoggedInMutationCommand[SmartListUpdateUseCase]):
    """UseCase for updating a smart list."""
