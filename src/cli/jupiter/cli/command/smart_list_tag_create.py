"""UseCase for creating a smart list tag."""

from jupiter.cli.command.command import LoggedInMutationCommand
from jupiter.core.use_cases.smart_lists.tag.create import (
    SmartListTagCreateUseCase,
)


class SmartListTagCreate(LoggedInMutationCommand[SmartListTagCreateUseCase]):
    """UseCase for creating a smart list tag."""
