"""UseCase for creating a smart list."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.create import (
    SmartListCreateUseCase,
)


class SmartListCreate(LoggedInMutationCommand[SmartListCreateUseCase]):
    """UseCase for creating a smart list."""
